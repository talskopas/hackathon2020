import time
import struct
import keyboard
from socket import *

print("Client started, listening for offer requests...")
# Servers broadcast their announcements with destination port 13117 
# client offers port must be this number
clientPort = 13117
clientOffersSocket = socket(AF_INET, SOCK_DGRAM)
clientOffersSocket.bind(('', clientPort))

while True:
    # get offer from some server
    message, (serverIP, serverPort) = clientOffersSocket.recvfrom(2048)
    magicCookie, messageType, TCPserverPort = struct.unpack('IBh', message)

    # checking cookie magic number
    if magicCookie == int("0xfeedbeef", 0):
        print("Received offer from", serverIP, ", attempting to connect...")

        # create TCP connection with the server 
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverIP, TCPserverPort))

        # send team name to the server
        teamName = "Hatovim\n".encode('ascii')
        clientSocket.send(teamName)

        # printing message from the server - the game is starting
        serverMSG = clientSocket.recv(1024).decode('ascii')
        print(serverMSG)

        # START OF THE GAME
        now = time.time()
        limit = now + 10
        # for 10 seconds, sends every character the client taps
        while time.time() < limit:
            char = 'a\n'.encode('ascii')
            clientSocket.send(char)
            time.sleep(10)

        # END OF THE GAME
        print("Server disconnected, listening for offer requests...")
        clientSocket.close()

clientOffersSocket.close()
