import time
import struct
import sys
import getch
import multiprocessing
from socket import *

# COLORS BONUS 
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print(bcolors.OKBLUE + "Client started, listening for offer requests..." + bcolors.ENDC)

# max size for reciving data
maxBufferSize = 1024

# Servers broadcast their announcements with destination port 13117 
# client offers port must be this number
clientPort = 13117
clientOffersSocket = socket(AF_INET, SOCK_DGRAM)
try:
    clientOffersSocket.bind(('', clientPort))
except:
    sys.exit(bcolors.WARNING + "Cannot Bind to Port " + str(clientPort) + bcolors.ENDC)
clientOffersSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# CLIENT RUNNING FOREVER
while True:
    # get offer from some server
    message, (serverIP, serverPort) = clientOffersSocket.recvfrom(maxBufferSize)
    try:
        magicCookie, messageType, TCPserverPort = struct.unpack('!IBH', message)
    except:
        print(bcolors.WARNING + "Unexcpted Offer Recieved - Waiting Again For Offers Message" + bcolors.ENDC)
        continue

    # checking cookie magic number
    if magicCookie == int("0xfeedbeef", 0):
        print(bcolors.OKGREEN + "Received offer from", serverIP, ", attempting to connect..." + bcolors.ENDC)

        # create TCP connection with the server 
        clientSocket = socket(AF_INET, SOCK_STREAM)
        try:
            clientSocket.connect((serverIP, TCPserverPort))
        except:
            print(bcolors.WARNING + "Cannot Connect To The Server - Waiting Again For Offers Message" + bcolors.ENDC)
            continue

        # send team name to the server
        teamName = "Hatovim\n".encode('ascii')
        clientSocket.send(teamName)

        # printing message from the server - the game is starting
        serverMSG = clientSocket.recv(maxBufferSize).decode('ascii')
        print(bcolors.OKGREEN + serverMSG + bcolors.ENDC)

        # START OF THE GAME
        def game_function():
            # ending after 10 seconds 
            while True:
                # get char from client command
                char = getch.getch()
                clientSocket.send(char.encode('ascii'))
        
        # running the game for 10 seconds
        game_thread = multiprocessing.Process(target=game_function)
        game_thread.start()
        time.sleep(10)
        game_thread.terminate()

        # get the results of the game and prints it
        gameEndMSG = clientSocket.recv(maxBufferSize).decode('ascii')
        print(bcolors.OKGREEN + gameEndMSG + bcolors.ENDC)

        # END OF THE GAME
        print(bcolors.OKBLUE + "Server disconnected, listening for offer requests..." + bcolors.ENDC)
        clientSocket.close()

clientOffersSocket.close()
