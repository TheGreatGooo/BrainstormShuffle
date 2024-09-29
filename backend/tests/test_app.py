import pytest
import json
import math

def test_duplicate_users(client):
    assert client.post("/register", json={'name':'u1','role':'FE'}).status_code == 201
    assert client.post("/register", json={'name':'u2','role':'FE'}).status_code == 201
    assert client.post("/register", json={'name':'u1','role':'FE'}).status_code == 400
    assert client.post("/register", json={'name':'u1','role':'BE'}).status_code == 400
    assert client.post("/register", json={'name':'admin','role':'admin'}).status_code == 400

def test_valid_initial_pairing(client):
    assert client.post("/register", json={'name':'u1','role':'FE'}).status_code == 201
    assert client.post("/register", json={'name':'u2','role':'FE'}).status_code == 201
    assert client.post("/next_round").status_code == 200
    u1State = client.get("/state?user=u1")
    u2State = client.get("/state?user=u2")
    assert u1State.json["table"] == 0
    assert u2State.json["table"] == 0
    assert u1State.json["seconds_remaining"] == 10*60

def test_round_start_odd_users(client):
    assert client.post("/register", json={'name':'u1','role':'FE'}).status_code == 201
    assert client.post("/register", json={'name':'u2','role':'FE'}).status_code == 201
    assert client.post("/register", json={'name':'u3','role':'FE'}).status_code == 201
    assert client.post("/next_round").status_code == 400

def test_valid_initial_pairing_with_100_users(client):
    for i in range(0,100):
        assert client.post("/register", json={'name':f'u{i}','role':'FE'}).status_code == 201
    round_response = client.post("/next_round")
    assert round_response.status_code == 200
    for pairing in round_response.json['pairings']:
        assert pairing['strategy'] == "INITIAL"
    tables = []
    already_assigned = []
    for i in range(0,50):
        tables.append([])
    for i in range(0,100):
        state = client.get(f"/state?user=u{i}")
        tables[state.json["table"]].append(i)
        assert state.json["seconds_remaining"] == 10*60
    for i in range(0,50):
        assert len(tables[i]) == 2

def valid_smart_paring(num_users, client):
    for i in range(0,num_users):
        assert client.post("/register", json={'name':f'u{i}','role':'FE'}).status_code == 201
    users_meeting = []
    for i in range(0,num_users):
        users_meeting.append([])
    for round_number in range(0,math.ceil(math.log2(num_users))):
        round_response = client.post("/next_round")
        assert round_response.status_code == 200
        full_state = client.get("/full_state").json
        print(full_state['influence_matrix'])
        print(full_state['rounds'][len(full_state['rounds'])-1])
        tables = []
        already_assigned = []
        for i in range(0,int(num_users/2)):
            tables.append([])
        for i in range(0,num_users):
            state = client.get(f"/state?user=u{i}")
            tables[state.json["table"]].append(i)
            assert state.json["seconds_remaining"] >= 599
        for i in range(0,int(num_users/2)):
            assert len(tables[i]) == 2
            assert tables[i][1] not in users_meeting[tables[i][0]]
            assert tables[i][0] not in users_meeting[tables[i][1]]
            users_meeting[tables[i][0]].append(tables[i][1])
            users_meeting[tables[i][1]].append(tables[i][0])

def test_valid_smart_pairing_with_6_users(client):
    num_users = 6
    valid_smart_paring(num_users, client)

def test_valid_smart_pairing_with_8_users(client):
    valid_smart_paring(8, client)

def test_valid_smart_pairing_with_10_users(client):
    valid_smart_paring(10, client)

def test_valid_smart_pairing_with_12_users(client):
    valid_smart_paring(12, client)

def test_valid_smart_pairing_with_14_users(client):
    valid_smart_paring(14, client)
def test_valid_smart_pairing_with_16_users(client):
    valid_smart_paring(16, client)
def test_valid_smart_pairing_with_18_users(client):
    valid_smart_paring(18, client)
def test_valid_smart_pairing_with_20_users(client):
    valid_smart_paring(20, client)
def test_valid_smart_pairing_with_22_users(client):
    valid_smart_paring(22, client)
def test_valid_smart_pairing_with_50_users(client):
    valid_smart_paring(50, client)
def test_valid_smart_pairing_with_100_users(client):
    valid_smart_paring(100, client)
