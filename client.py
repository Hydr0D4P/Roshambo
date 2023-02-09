import threading
from socket import *

nickname = input("Choose a nickname: ")

# AF_INET = Internet domain, SOCK_STREAM = TCP. TCP er slow but steady i forhold til UDP.
client = socket(AF_INET,SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

"""
recieve lytter etter meldinger fra server. Server er definert som client i denne situasjonen siden den oppfører seg
som en klient. hvis meldingen fra server er NICK, så autosendes nickname.
"""

def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            if message == 'NICK':
                client.send(nickname.encode())
            else:
                print(message)
        except:
            print("An error occurred!")
            client.close()
            break


"""
write() sender ting fra brukeren til serveren. message er formatert først, så deformatert. Dette er sykt teit og skaper
2000 problemer men jeg er veldig sta. 
Leser input, sjekker om det er en kommando, hvis det, sjekk hvilken, hvis ikke, send menldingen. det er en stor try
og jeg har ikke fått trigget den enda, men den er fin å ha hvis ting går skjeis i guess.
"""
def write():
    while True:
        # leser etter input fra brukeren, setter så nicknamet forran
        message = f"{nickname}: {input('')}"
        # for å kunne lese commands uten å sende til server først, sjekker vi om meldingen starter med /.
        try:
            # len(nickname)+2 sikrer oss at vi kommer til starten av meldigen, og hopper over "nickname: "
            if message[len(nickname)+2:].startswith('/'):
                # hvis funnet, sjekk om det er følgende kommandoer
                if message[len(nickname)+2:].startswith('/queue'):
                    # hvis kommandoen er funnet send en melding som server kan lete etter senere
                    client.send("QRPS".encode())
                    print("Remember to set a move with /move (r/p/s)")
                elif message[len(nickname)+2:].startswith('/move'):
                    changemove(message[len(nickname) + 2 + 6:])
                else:
                    print(f"({message[len(nickname)+2:]}) is not a valid command!")
            else:
                # Hvis ikke en kommando, er det er melding. Send meldingen til server (serveren er en client)
                client.send(message.encode())
        except:
            print(f"ERROR: Command ({message}) is invalid!")
        # hvis kommandoen ikke finnes, eller er skrevet uten parameter vil denne exception skrives ut.

# Validerer og sender trekk i MOVE format.
def changemove(move):
    if move not in ("r","p","s"):
        print("Invalid move")
        return
    rpsmove = f"MOVE {move}"
    client.send(rpsmove.encode())


# Starter 2 threads, en for recieve, og en for write
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()