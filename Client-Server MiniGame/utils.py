import random
import msvcrt
import time
import sys


def isValidName(name):
    return 1 < len(name) < 10 and name.isalnum()

def sendToOne(clientList, receiver, message):
    try:
        receiver.send(bytes(message, 'utf-8'))
    except:
        receiver.close()
        clientList.remove(receiver)


def broadcast(clientList, message):
    for sock in clientList:
        try:
            sock.send(bytes(message, 'utf-8'))
        except:
            sock.close()
            clientList.remove(sock)


def receive_message(client_socket):
    message = client_socket.recv(1024).decode('utf-8')
    return message


def GenerateQuestion():
    opts = ['+', '-', '*', '/', '%']
    opIndex = random.randint(0, 4)  # + - * / %
    if opIndex == 0:
        num1 = random.randint(-10000, 10000)
        num2 = random.randint(-10000, 10000)
        answer = num1 + num2
    elif opIndex == 1:
        num1 = random.randint(-10000, 10000)
        num2 = random.randint(-10000, 10000)
        answer = num1 - num2
    elif opIndex == 2:
        num1 = random.randint(-40, 40)
        num2 = random.randint(-40, 40)
        answer = num1 * num2
    elif opIndex == 3:
        num1 = random.randint(-10000, 10000)
        num2 = random.randint(2, 10)
        answer = int(num1 / num2)
    else:
        num1 = random.randint(-10000, 10000)
        num2 = random.randint(2, 10)
        answer = num1 % num2

    question = ""
    if num2 > -1:
        question = str(num1) + " " + opts[opIndex] + " " + str(num2)
    else:
        question = str(num1) + " " + opts[opIndex] + " (" + str(num2) + ")"
    return question, answer


def CompareResult(mess, answer):
    try:
        mess = int(mess)
    except:
        return False
    if mess == answer:
        return True
    return False


# source: https://stackoverflow.com/questions/15528939/time-limited-input/15533404#15533404

def input_with_timeout(prompt, timeout, timer=time.monotonic):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    endtime = timer() + timeout
    result = []
    while timer() < endtime:
        if msvcrt.kbhit():
            result.append(msvcrt.getwche())
            if result[-1] == '\r' or result[-1] == '\n':
                return ''.join(result[:-1])
            if ord(result[-1]) == 8:
                result = result[:-2]
        time.sleep(0.04)  # not important
    return "None"
