import json
class Brainstorm:
    def __init__(self, influence_matrix, users=[], rounds=[], state=0):
        self.users = users
        self.rounds = rounds
        self.state = state
        self.influence_matrix = influence_matrix
    def toDict(self):
        return {"influence_matrix":self.influence_matrix,"users":[x.toDict() for x in self.users],"rounds":[x.toDict() for x in self.rounds], "state":self.state}
class Round:
    def __init__(self, timestamp, pairings=[]):
        self.pairings = pairings
        self.timestamp = timestamp
    def toDict(self):
        return {"timestamp":self.timestamp,"pairings":[x.toDict() for x in self.pairings]}
class User:
    def __init__(self, name, role):
        self.name = name
        self.role = role
    def toDict(self):
        return self.__dict__
class Pairing:
    def __init__(self, user1, user1_rotation_count, user2, user2_rotation_count, table, strategy):
        self.user1 = user1
        self.user2 = user2
        self.table = table
        self.user1_rotation_count = user1_rotation_count
        self.user2_rotation_count = user2_rotation_count
        self.strategy = strategy
    def toDict(self):
        return self.__dict__
