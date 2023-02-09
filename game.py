import server

def newgame(p1, p2):
    print("ok this is epic")
    server.broadcast(f"{p1} and {p2} are playing Roshambo!")




def __init__(self, id):
    self.p1Went = False
    self.p2Went = False
    self.active = False
    self.id = id
    self.moves = [None, None]
    self.wins = [0,0]
    self.ties = 0

def get_player_move(self, p):
    return self.moves[p]

def player(self, player, move):
    self.moves[player] = move
    if player == 0:
        self.p1Went = True
    else:
        self.p2Went = True

def bothWent(self):
    return self.p1Went and self.p2Went

def winner(self):
    p1 = self.moves[0].upper()[0]
    p2 = self.moves[1].upper()[0]

    winner = -1

    if p1 == "r" and p2 == "s":
        winner = 0
    elif p1 == "r" and p2 == "p":
        winner = 1
    elif p1 == "p" and p2 == "r":
        winner = 0
    elif p1 == "p" and p2 == "s":
        winner = 1
    elif p1 == "s" and p2 == "p":
         winner = 0
    elif p1 == "s" and p2 == "r":
        winner = 1
    return winner

def resetWent(self):
    self.p1Went = False
    self.p2Went = False