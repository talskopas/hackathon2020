import time
import struct
import concurrent.futures
from threading import *
from socket import *

print("Server started, listening on IP address 172.1.0.4")

# creating UDP socket for sending offers
serverOffersSocket = socket(AF_INET, SOCK_DGRAM)

# creating TCP socket for accept clients
serverPort = 25000
serverConnectionSocket = socket(AF_INET, SOCK_STREAM)
serverConnectionSocket.bind(('', serverPort))

# two arrays of groups - each team in the group contains (teamName, socket) 
group1 = []
group2 = []

def offer_thread_function():
    # create offer to be send
    magicCookie = int("0xfeedbeef", 0)
    messageType = int("0x2", 0)
    offer = struct.pack('!IBH', magicCookie, messageType, serverPort)

    # sending offers until the 10 seconds timer will pass
    for i in range(10):
        serverOffersSocket.sendto(offer, ("localhost", 13118))
        time.sleep(1)

def set_up_game_function():
    # accepting clients until the 10 seconds timer will pass 
    serverConnectionSocket.settimeout(10)
    serverConnectionSocket.listen(1)
    groupFlag = False

    while True:
        try:
            # wait until client is trying to connect and get his team name
            connectionSocket, addr = serverConnectionSocket.accept()
            teamName = connectionSocket.recv(1024).decode('ascii')
            # adding client to group1 or group2
            if groupFlag:
                group1.append((teamName, connectionSocket))
            else:
                group2.append((teamName, connectionSocket))
            groupFlag = not groupFlag 
        # catching exception when the socket gets timeout - after 10 seconds
        except:
            break  

def client_thread(client_socket, game_start_MSG):
    # the is played for 10 seconds
    client_socket.settimeout(10)
    pressing_counter = 0
    
    # send starting message to the client
    client_socket.send(game_start_MSG.encode('ascii'))
    
    # taps detector until the client stop sending - after 10 seconds
    while True:  
        try:
            # getting client taps
            char = client_socket.recv(1024).decode('ascii')
            pressing_counter += 1
        except:
            break
    client_socket.close()
    return pressing_counter

def game_threads_function():
    # creating starting message that will be send to all clients
    game_start_MSG = "Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"
    for (teamName, client_socket) in group1:
        game_start_MSG += teamName + "\n"
    game_start_MSG += "Group 2:\n==\n" 
    for (teamName, client_socket) in group2:
        game_start_MSG += teamName + "\n"
    game_start_MSG += "Start pressing keys on your keyboard as fast as you can!!"

    # counters for group1 and group2
    group1_pressing_counter = 0
    group2_pressing_counter = 0

    # creating and starting thread for each client
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        for (teamName, client_socket) in group1:
            future = executor.submit(client_thread, client_socket, game_start_MSG)
            group1_pressing_counter += future.result()
        for (teamName, client_socket) in group2:
            future = executor.submit(client_thread, client_socket, game_start_MSG)
            group2_pressing_counter += future.result()
    
    # END OF THE GAME MSG
    game_end_MSG = "Game over!\nGroup 1 typed in " + str(group1_pressing_counter) + " characters. Group 2 typed in " + str(group2_pressing_counter) + " characters.\n"
    if group1_pressing_counter > group2_pressing_counter:
        game_end_MSG += "Group 1 wins!\nCongratulations to the winners:\n==\n"
        for (teamName, client_socket) in group1:
            game_end_MSG += teamName + "\n"
    else:
        game_end_MSG += "Group 2 wins!\nCongratulations to the winners:\n==\n"
        for (teamName, client_socket) in group2:
            game_end_MSG += teamName + "\n"
    print(game_end_MSG)



# MAIN INFINITY LOOP
while True:
    # creating and starting the offer and connect threads
    offer_thread = Thread(target=offer_thread_function)
    set_up_game_thread = Thread(target=set_up_game_function)
    offer_thread.start()
    set_up_game_thread.start()

    # waiting 10 seconds for then
    offer_thread.join()
    set_up_game_thread.join()

    # starting the game!
    game_threads_function()

    # end of the game
    print("Game over, sending out offer requests...")

    # initialize the two arrays of groups for next round 
    group1 = []
    group2 = []

serverOffersSocket.close()
serverConnectionSocket.close()
        