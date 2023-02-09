import threading
from socket import *
import time

host = '127.0.0.1'  # Localhost
port = 55555

server = socket(AF_INET,SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []
rpsqueue = []
moves = []


def broadcast(message):
    for client in clients:
        client.send(f"[{now()}] {message}".encode())


"""
handle() passer på at hvis en meldling blir sendt, så kommer den til serverern. client.recv(1024) lytter bare etter
meldinger sendt fra client. det er også noen if statements som passer på om kommandoer kommer inn, og gjør det de skal.
hvis det ikke var en kommando så sendes meldingen.

Noe innteresant er at hvis en bruker dissconnecter så telles dette som en error. Dette kan faktisk brukes til å finne
ut om en bruker må eller har DC'et. når en error oppstår, blir handleren drept. og client og nick oppdatert.
"""
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if message.decode().startswith('QRPS'):
                rpsqueue.append(client)
                if len(rpsqueue) == 1:
                    broadcast(f"{getnickfromclient(client)} Wants to play Roshambo! (/queue to join)")
                else:
                    print(
                        f"Game Starting between {getnickfromclient(rpsqueue[0])} and {getnickfromclient(rpsqueue[1])}."
                    )
                    game_thread = threading.Thread(target=game, args=(rpsqueue[0], rpsqueue[1],))
                    game_thread.start()
            elif message.decode().startswith('MOVE'):
                decoded_move = message.decode()
                user_move = Move(client, f"{decoded_move[5:]}")
                moves.append(user_move)
            else:
                broadcast(message.decode())
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            print(f"{nickname} disconnected from the server")
            broadcast(f"//{nickname} left the chat!//")
            nicknames.remove(nickname)
            break


"""
recieve leter kun etter nye clients og henter ut nickname. etterpå legger den de til i nicknames[] og clients[].
de har begge samme indeks siden de legges til sammtidig. kunne lagdt objekter her også. starter en new "instance"
eller en handler.
"""
def recieve():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('NICK'.encode())
        nickname = client.recv(1024).decode()

        print(f"Nickname of the client {str(address)} is {nickname}!")
        broadcast(f"//{nickname} joined the chat!//".encode().decode())
        client.send('//Connected to the server!//'.encode())

        nicknames.append(nickname)
        clients.append(client)

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

# tid i TMS format
def now():
    # current time
    t = time.localtime()
    return time.strftime("%H:%M:%S", t)


# gets nick from client. Dette gjøres ved å bruke client sin index siden den er det samme som nicknames.
def getnickfromclient(client):
    return nicknames[clients.index(client)]

"""
Hovedspillet. TLDR: tar to brukere fra queue som input, og venter på MOVE som blir sendt hvis brukeren skriver
/move. client.write() leter alltid etter ord som starter på / og sender parametere fra kommandoer direkte uten
brukernavn. Disse legges som et objekt Move() i moves[]. det ligger en for løkke som ser etter alle moves som matcher
med en client ip i game. dette betyr i praksis at flere spillere kan spille samtidig. 

suspencemaker() skriver bare ut litt moroe ting for å lage litt "suspence". kun kosmetisk, kunne egentlig være client
side for å redusere load osv. men men.

sjekker så med 6 if statements om hvordan spillet endet, hvis spillet endet uavgjordt returner, hvis ikke skrives
vinnerern ut.
"""
def game(p1, p2):
    broadcast(f"{getnickfromclient(p1)} and {getnickfromclient(p2)} are playing Roshambo!")
    rpsqueue.clear()


    p1_move = ""
    p2_move = ""
    while p1_move == "" or p2_move == "":
        for move in moves:
            if move.user == p1:
                p1_move = move.move
            if move.user == p2:
                p2_move = move.move
        time.sleep(0.5)


    print(f"moves detected [{p1_move},{p2_move}]")
    winner = -1

    suspencemaker(p1, p1_move, p2, p2_move)

    if p1_move == "r" and p2_move == "s":
        winner = getnickfromclient(p1)
        broadcast("Rock crushes Scissors!")
    elif p1_move == "r" and p2_move == "p":
        winner = getnickfromclient(p2)
        broadcast("Paper covers Rock!")
    elif p1_move == "p" and p2_move == "r":
        winner = getnickfromclient(p1)
        broadcast("Paper covers Rock!")
    elif p1_move == "p" and p2_move == "s":
        winner = getnickfromclient(p2)
        broadcast("Scissors cuts Paper!")
    elif p1_move == "s" and p2_move == "p":
        winner = getnickfromclient(p1)
        broadcast("Scissors cuts Paper!")
    elif p1_move == "s" and p2_move == "r":
        winner = getnickfromclient(p2)
        broadcast("Rock crushes Scissors!")
    if winner == -1:
        broadcast(f"Game between {getnickfromclient(p1)} and {getnickfromclient(p2)} ended in a draw!")
        return
    broadcast(
        f"{getnickfromclient(p1)} played against {getnickfromclient(p2)} where"
        f" {winner} Won!")

    moves.clear()


def suspencemaker(p1,p1m,p2,p2m):
    move1 = movetostring(p1m)
    move2 = movetostring(p2m)
    sendbothplayers(p1,p2,f"Let the Battle Commence")
    time.sleep(1)
    sendbothplayers(p1,p2,f"Rock!")
    time.sleep(0.5)
    sendbothplayers(p1,p2,f"Paper!")
    time.sleep(0.5)
    sendbothplayers(p1,p2,f"Scissors!")
    time.sleep(0.5)
    sendbothplayers(p1,p2,f"Shoot!")
    time.sleep(0.5)
    p1.send(f"You Picked {move1}".encode())
    p2.send(f"You Picked {move2}".encode())
    time.sleep(1)
    p1.send(f"They Picked {move2}".encode())
    p2.send(f"They Picked {move1}".encode())
    time.sleep(0.25)

"""
r = Rock
p = Paper
s = Scissors
ville bare ha en separat kommando for dette, sparer meg 2 linjer men så så
"""
def movetostring(move):
    if (move == "r"): return "Rock"
    if (move == "p"): return "Paper"
    if (move == "s"): return "Scissors"


""""
noen ganger må samme melding sendes til begge spillerne, det er fint å ha en kommando som gjør dette"""
def sendbothplayers(p1,p2,string):
    p1.send(string.encode())
    p2.send(string.encode())

""""
en class Move. inneholder brukeren og trekket. Kunne gjordt dette for nickname også men jeg er lat og allerede har kodet
det og er livredd det skal gå i stykker.
"""
class Move:
    def __init__(self, user, move):
        self.user = user
        self.move = move


# starter første recieve() med en melding til konsoll for å vise at alt er 200 ok
print("Server is listening...")
recieve()