import socket
from _thread import start_new_thread
from utils import *
import time

number_of_players = int(input("Please enter the number of players(max allowed is 10): "))
# number_of_players = 2
if number_of_players > 10 or number_of_players < 2:
    while number_of_players > 10 or number_of_players < 2:
        number_of_players = int(input("Please input valid number: "))

# race_length = 3
race_length = int(input("Please enter the race length(value between 3 and 26): "))
if race_length > 26 or race_length < 3:
    while race_length > 26 or race_length < 3:
        race_length = int(input("Please input valid number: "))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
server.settimeout(1000)

IP_address = 'localhost'
Port = 9099
server.bind((IP_address, Port))
server.listen(100)

while True:
    print("Server start listening ....")
    clientList = []
    playerList = {}
    answerList = {}
    scoreList = {}
    num_health = {}
    number_joined = 0
    startGame = False
    answerOrder = []


    def startClientThread(clientSocket, address):
        global number_joined
        global playerList
        global clientList
        global scoreList
        global startGame
        global answerList
        global answerOrder
        while True:
            name = clientSocket.recv(2048).decode('utf-8')
            if name:
                if name in playerList.values():
                    sendToOne(clientList, clientSocket, "Name already taken")
                else:
                    playerList[clientSocket] = name
                    scoreList[name] = 0
                    num_health[name] = 3
                    number_joined += 1
                    print("Player connected: " + str(address) + " [ " + playerList[clientSocket] + " ]")
                    if number_joined < number_of_players:
                        sendToOne(clientList, clientSocket,
                                  "Welcome to the quiz " + name + "!\nPlease wait for other participants to join...")
                        break
                    elif number_joined == number_of_players:
                        startGame = True
                        break
        while True:
            try:
                message = clientSocket.recv(2048).decode('utf-8')
                if message:
                    print(playerList[clientSocket] + " answered:" + message)
                    answerList[clientSocket] = message
                    answerOrder.append(clientSocket)
            except:
                print("Player disconnected")
                break


    def gamePlay():
        global answerOrder
        broadcast(clientList, "\nParticipant(s) joined:")
        for i in playerList:
            broadcast(clientList, ">> " + playerList[i] + "\n")
        broadcast(clientList, "\nThe quiz will begin in 20 seconds. Quickly go through the instructions\n")
        broadcast(clientList, f"RL|{race_length}")
        print("\n" + str(
            number_of_players) + " participant(s) connected! The quiz will begin in 20 seconds\n\nRace length is " +
              str(race_length) + "\n")
        time.sleep(20)
        broadcast(clientList, "start game")
        time.sleep(0.5)
        print("Start game...")
        num_player_left = number_of_players
        end_game = False
        while True:
            question, answer = GenerateQuestion()
            print(question, answer)
            for i in answerList.keys():
                answerList[i] = "None"
            broadcast(clientList, "Q|" + question)
            time.sleep(20)
            broadcast(clientList, "A|" + str(answer))
            time.sleep(2)
            clientSockToRemove = None
            scoreNameList = []
            totalScoreLost = 0
            answerWrongList = []
            answerRightList = []

            for clientSock in answerList.keys():
                if (CompareResult(answerList[clientSock], answer)):
                    answerRightList.append(clientSock)
                else:
                    answerWrongList.append(clientSock)

            if len(answerList.keys()) > 0:
                if (len(answerRightList) == 0):
                    firstRightPlayer = None
                else:
                    for sock in answerOrder:
                        if sock in answerRightList:
                            firstRightPlayer = sock
                            break
                answerOrder = []

            for clientSock in answerList.keys():
                if clientSock in answerRightList:
                    if clientSock == firstRightPlayer:
                        plusPoint = max(len(answerWrongList), 1)
                        print("First right player got " + str(plusPoint))
                        scoreList[playerList[clientSock]] += plusPoint
                    else:
                        scoreList[playerList[clientSock]] += 1
                    scoreNameList.append((clientSock, scoreList[playerList[clientSock]]))
                    sendToOne(clientList, clientSock,
                              "S|" + str(scoreList[playerList[clientSock]]))

                    if scoreList[playerList[clientSock]] >= race_length:
                        time.sleep(1)
                        sendToOne(clientList, clientSock, "Win")
                        time.sleep(0.2)
                        for soc in clientList:
                            if soc != clientSock:
                                sendToOne(clientList, soc, "Gameover")
                                clientList.remove(soc)
                        end_game = True
                        break  # stop the game

                else:
                    if scoreList[playerList[clientSock]] > 0:
                        scoreList[playerList[clientSock]] -= 1
                        totalScoreLost += 1
                    num_health[playerList[clientSock]] -= 1
                    sendToOne(clientList, clientSock,
                              "MS|" + str(scoreList[playerList[clientSock]]) + "|L|"
                              + str(num_health[playerList[clientSock]]))

                    if num_health[playerList[clientSock]] == 0:
                        time.sleep(1)
                        broadcast(clientList, "Player " + playerList[clientSock] + " is out. There are " + str(
                            num_player_left) + " players left\n")
                        time.sleep(1)
                        sendToOne(clientList, clientSock, "Gameover")
                        clientList.remove(clientSock)
                        clientSockToRemove = clientSock
                        num_player_left -= 1
                        if num_player_left == 0:
                            print("All players are out. The game finished!!!!")
                            end_game = True
                            break
                    else:
                        time.sleep(1)
                        scoreNameList.append((clientSock, scoreList[playerList[clientSock]]))

            if not end_game:
                time.sleep(0.5)
                scoreNameList.sort(key=lambda x: x[1], reverse=True)
                for i in range(len(scoreNameList)):
                    if i == 0:
                        sendToOne(clientList, scoreNameList[i][0], "Top")
                    else:
                        sendToOne(clientList, scoreNameList[i][0],
                                  "P|" + str(i + 1) + "|B|" + playerList[scoreNameList[i - 1][0]])
                time.sleep(3)
                broadcast(clientList, "end of announcement")
                time.sleep(0.5)
                if clientSockToRemove:
                    answerList.pop(clientSockToRemove)
                    clientSockToRemove = None
            else:
                break


    numConnections = 0
    while True:
        if numConnections < number_of_players:
            clientSocket, address = server.accept()
            if number_joined == number_of_players:
                sendToOne(clientSocket, "Maximum number of players joined!")
                clientSocket.close()
            numConnections += 1
            clientList.append(clientSocket)
            print(address[0] + " connected")
            start_new_thread(startClientThread, (clientSocket, address,))
        elif startGame:
            break

    gamePlay()
