from flask import Flask, request, jsonify, Blueprint
from .models import db, AuditLog, IdeaLog
from .brainstorm import Brainstorm, User, Pairing, Round
import random
import time
import json
api = Blueprint('api', __name__)
brainstorm = None
ADMIN = User("admin","admin")
#actions
USER_REGISTERED = 0
ADMIN_ROUND_START = 1
ADMIN_ROUND_END = 2
ADMIN_END_ROUNDS = 3
#states
NOT_STARTED = 0
NEXT_ROUND_START = 1
WAITING_FOR_NEXT_ROUND = 2
FIN = 3

def update_local_state(audit_log):
    global brainstorm
    if audit_log.action_id == USER_REGISTERED :
        user_json = json.loads(audit_log.action_data)
        brainstorm.users.append(User(user_json['name'], user_json['role']))
    elif audit_log.action_id == ADMIN_ROUND_START :
        print("round start")
        round_json = json.loads(audit_log.action_data)
        pairings = []
        for pairing_json in round_json['pairings']:
            pairings.append(Pairing(pairing_json['user1'], pairing_json['user1_rotation_count'], pairing_json['user2'], pairing_json['user2_rotation_count'], pairing_json['table'], pairing_json['strategy']))
        brainstorm.rounds.append(Round(round_json['timestamp'], pairings))
        brainstorm.state = NEXT_ROUND_START
    elif audit_log.action_id == ADMIN_ROUND_END :
        brainstorm.state = WAITING_FOR_NEXT_ROUND
    elif audit_log.action_id == ADMIN_END_ROUNDS :
        brainstorm.state = FIN

def reload_state():
    global brainstorm
    audit_logs = AuditLog.query.all()
    brainstorm = Brainstorm([[0 for x in range(1)] for y in range(1)], [], [], NOT_STARTED )
    for audit_log in audit_logs:
        update_local_state(audit_log)

def log_audit(action_id, action_data, user_name):
    audit_log = AuditLog(action_id=action_id, action_data=json.dumps(action_data), user_name=user_name)
    db.session.add(audit_log)
    db.session.commit()
    update_local_state(audit_log)

def get_table_to_use(user_id, user2_id, users, user_rotation_counts, previous_user_table, table_assigned):
    user1_rotation_count = user_rotation_counts[users[user_id].name]
    user2_rotation_count = user_rotation_counts[users[user2_id].name]
    if previous_user_table[users[user_id].name] in table_assigned and previous_user_table[users[user2_id].name] in table_assigned:
        all_tables = []
        for k,v in previous_user_table.items():
            all_tables.append(v)
        table_to_use = list(set(all_tables) - set(table_assigned))[0]
        user1_rotation_count = user1_rotation_count + 1
        user2_rotation_count = user2_rotation_count + 1
    elif previous_user_table[users[user_id].name] in table_assigned:
        table_to_use = previous_user_table[users[user2_id].name]
        user1_rotation_count = user1_rotation_count + 1
    elif previous_user_table[users[user2_id].name] in table_assigned:
        table_to_use = previous_user_table[users[user_id].name]
        user2_rotation_count = user2_rotation_count + 1
    elif user1_rotation_count > user2_rotation_count :
        table_to_use = previous_user_table[users[user_id].name]
        user2_rotation_count = user2_rotation_count + 1
    else:
        table_to_use = previous_user_table[users[user2_id].name]
        user1_rotation_count = user1_rotation_count + 1
    return table_to_use, user1_rotation_count, user2_rotation_count

def register_user(new_user):
    if new_user.name == "admin":
        return jsonify({"msg":"Username already taken, please use another"}), 400
    for user in brainstorm.users:
        if new_user.name == user.name:
            return jsonify({"msg":"Username already taken, please use another"}), 400
    log_audit(USER_REGISTERED, new_user.toDict(), new_user.name)
    return jsonify(new_user.toDict()), 201

@api.route('/register', methods=['POST'])
def register():
    data = request.json
    new_user = User(name=data['name'], role=data['role'])
    return register_user(new_user)

@api.route('/login', methods=['POST'])
def login():
    data = request.json
    new_user = User(name=data['name'], role=data['role'])
    if new_user.name == "admin":
        return jsonify({"msg":"Username admin cannot be logged into, please use another"}), 400
    for user in brainstorm.users:
        if new_user.name == user.name:
            return jsonify(user.toDict()), 201
    return jsonify({"msg":"Username not found"}), 400

@api.route('/idea', methods=['POST'])
def idea():
    data = request.json

    result = db.session.query(IdeaLog).filter(IdeaLog.user_name == data['user_name']).order_by(IdeaLog.timestamp.desc()).first()

    if (result is None):
        idea_log = IdeaLog(user_name=data['user_name'], idea=data['idea'])
        db.session.add(idea_log)
        db.session.commit()
        return jsonify(data), 200
    else:
        result.idea = data['idea']
        db.session.commit()
        return jsonify(result.toDict()), 200

@api.route('/idea', methods=['GET'])
def idea_get():
    user_name = request.args.get("user_name")

    result = db.session.query(IdeaLog).filter(IdeaLog.user_name == user_name).order_by(IdeaLog.timestamp.desc()).first()

    if (result is None):
        return jsonify({}), 204
    else:
        return jsonify(result.toDict()), 200


@api.route('/next_round', methods=['POST'])
def start_round():
    users = brainstorm.users
    if not users:
        return jsonify({'error': 'No users registered'}), 400
    print(f"Round requested to start with {len(users)} users")
    if len(users)%2 != 0 :
        return jsonify({'error': f'Need an even number of users, currently there are {len(users)}'}), 400
    if brainstorm.state == NOT_STARTED:
        # first round
        brainstorm.influence_matrix = [[0 for x in range(len(users))] for y in range(len(users))]
        random.shuffle(users)
        pairs = []
        next_free_table = 0
        for i in range(0, len(users), 2):
            if i + 1 < len(users):
                pair = Pairing(users[i].name, 1, users[i + 1].name, 1, next_free_table, "INITIAL")
                next_free_table = next_free_table + 1
                pairs.append(pair)
                brainstorm.influence_matrix[i][i+1] = 2
                brainstorm.influence_matrix[i][i] = 2
                brainstorm.influence_matrix[i+1][i] = 2
                brainstorm.influence_matrix[i+1][i+1] = 2
    else:
        #smart shuffle
        previous_round = brainstorm.rounds[len(brainstorm.rounds)-1]
        user_rotation_counts = {}
        previous_user_table = {}
        for pairing in previous_round.pairings:
            user_rotation_counts[pairing.user1] = pairing.user1_rotation_count
            user_rotation_counts[pairing.user2] = pairing.user2_rotation_count
            previous_user_table[pairing.user1] = pairing.table
            previous_user_table[pairing.user2] = pairing.table
        already_assigned = []
        table_assigned = []
        pairs = []
        table_users = {}
        user_name_to_id = {}
        for user_id in range(0, len(users)):
            user_name_to_id[users[user_id].name] = user_id
        #brute force a good enough solution
        search_pairs = recursive_pair_search([],[],brainstorm.influence_matrix)
        pairs = []
        table_assigned = []
        already_assigned= []
        for pair in search_pairs:
            user1_id = pair[0]
            user2_id = pair[1]
            table_to_use, user1_rotation_count, user2_rotation_count = get_table_to_use(user1_id, user2_id, users, user_rotation_counts, previous_user_table, table_assigned)
            pairs.append(Pairing(users[user1_id].name, user1_rotation_count, users[user2_id].name, user2_rotation_count, table_to_use, "BRUTE-FORCE"))
            already_assigned.append(user_id)
            already_assigned.append(user2_id)
            table_assigned.append(table_to_use)

        #update the influence matrix
        for pair in pairs:
            user_id = user_name_to_id[pair.user1]
            user2_id = user_name_to_id[pair.user2]
            brainstorm.influence_matrix[user_id][user2_id] = 2
            brainstorm.influence_matrix[user2_id][user_id] = 2
            for influencer_id in range(0, len(users)):
                brainstorm.influence_matrix[user_id][influencer_id] = max(min(max(brainstorm.influence_matrix[user_id][influencer_id], brainstorm.influence_matrix[user2_id][influencer_id]), 1), brainstorm.influence_matrix[user_id][influencer_id])
                brainstorm.influence_matrix[user2_id][influencer_id] = max(min(max(brainstorm.influence_matrix[user_id][influencer_id], brainstorm.influence_matrix[user2_id][influencer_id]), 1), brainstorm.influence_matrix[user2_id][influencer_id])
    round = Round(int(time.time()), pairs)
    log_audit(ADMIN_ROUND_START, round.toDict(), ADMIN.name)
    return jsonify(round.toDict()), 200

def recursive_pair_search(already_used, selected_pairs, influence_matrix):
    if len(already_used) == len(influence_matrix):
        return selected_pairs
    for user1_id in range(0, len(influence_matrix)):
        if user1_id in already_used:
            continue
        priortized_selections = []
        priortized_selections.append([])
        priortized_selections.append([])
        priortized_selections.append([])
        for user2_id in range(0, len(influence_matrix)):
            if user1_id == user2_id or user2_id in already_used:
                continue
            priortized_selections[influence_matrix[user1_id][user2_id]].append(user2_id)
        for priority in range(0,2):
            for user2_id in priortized_selections[priority]:
                if influence_matrix[user1_id][user2_id] < 2:
                    #try out this match
                    already_used.append(user1_id)
                    already_used.append(user2_id)
                    selected_pairs.append([user1_id, user2_id])
                    resursive_search_result = recursive_pair_search(already_used, selected_pairs, influence_matrix)
                    if resursive_search_result is None:
                        already_used.pop()
                        already_used.pop()
                        selected_pairs.pop()
                    else:
                        return resursive_search_result
    return None


@api.route('/end_round', methods=['POST'])
def end_round():
    log_audit(ADMIN_ROUND_END, "{}", ADMIN.name)
    return jsonify({'message': 'Round ended'}), 200

@api.route('/complete', methods=['POST'])
def complete():
    log_audit(ADMIN_END_ROUNDS, "{}", ADMIN.name)
    return jsonify({'message': 'Round ended'}), 200

@api.route('/state', methods=['GET'])
def user_state():
    user_name = request.args.get("user")
    resp = {}
    resp['user'] = user_name
    resp['state'] = brainstorm.state
    if brainstorm.state == NEXT_ROUND_START :
        current_round = brainstorm.rounds[len(brainstorm.rounds)-1]
        for pairing in current_round.pairings :
            if pairing.user1 == user_name or pairing.user2 == user_name :
                resp['table'] = pairing.table
        resp['seconds_remaining'] = max(0, (current_round.timestamp + 10*60) - int(time.time()))
    return jsonify(resp), 200

@api.route('/full_state', methods=['GET'])
def full_state():
    return jsonify(brainstorm.toDict()), 200
