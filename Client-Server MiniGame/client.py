import enum
import socket
import sys
from _thread import start_new_thread
from enum import Enum
import pygame as pg
import utils
from threading import Thread
import select

from utils import isValidName, receive_message, input_with_timeout

Host = 'localhost'
Port = 9099


class GameState(Enum):
    LOGIN = 0
    WAITING = 1
    STARTING = 2
    STARTED = 3
    OVER = 4
    WIN = 5


# global variable
nickname = ''
notice = '~Please input your name~'
question = ''
answer = ''
score = 0
life = '3'
game_state = GameState.LOGIN
race_length = 0
result = ''
rank = ''

# init pygame
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 675
pg.init()
screen = pg.display.set_mode((1200, 675))
pg.display.set_caption("RacingArena")
logo_img = pg.image.load('resource/logo_icon.png')
background = pg.image.load('resource/logo.png')
pg.display.set_icon(logo_img)
font = pg.font.Font('resource/FiraCode-Regular.ttf', 32)
title_font = pg.font.Font('resource/FiraCode-Regular.ttf', 100)
question_font = pg.font.Font('resource/FiraCode-Bold.ttf', 72)
instruction_font = pg.font.Font('resource/FiraCode-Bold.ttf', 28)
life_font = pg.font.Font('resource/webdings.ttf', 72)
over_font = pg.font.Font('resource/FiraCode-Bold.ttf', 100)

# myColor
darkBlue = (67, 75, 231)
lightBlue = (61, 122, 255)
darkerBlue = (5, 35, 89)
whiteBlue = (104, 202, 249)
lighterBlue = (59, 166, 245)
orange = (255, 194, 134)
yellow = (255, 241, 175)
whiteRed = (247, 74, 62)


def render_login_scene():
    # (width, height)
    screen.blit(background, (0, 0))

    render_notice = font.render(notice, True, orange)
    notice_rect = render_notice.get_rect(center=(int(0.5 * SCREEN_WIDTH),
                                                 int(0.65 * SCREEN_HEIGHT)))
    screen.blit(render_notice, notice_rect)

    render_nickname = font.render(nickname, True, lighterBlue)
    nickname_rect = render_nickname.get_rect(center=(int(0.5 * SCREEN_WIDTH),
                                                     int(0.75 * SCREEN_HEIGHT)))
    screen.blit(render_nickname, nickname_rect)

    # (left, top) (width, height)
    input_box = pg.Rect((445, 490), (300, 1))
    input_box.center = (int(0.5 * SCREEN_WIDTH), int(0.75 * SCREEN_HEIGHT) + 20)
    pg.draw.rect(screen, lightBlue, input_box)

    render_instruction = font.render('Press Space to Start', True, lighterBlue)
    instruction_rect = render_instruction.get_rect(center=(int(SCREEN_WIDTH / 2),
                                                           int(0.9 * SCREEN_HEIGHT)))
    screen.blit(render_instruction, instruction_rect)


def render_waiting_scene():
    screen.fill(darkerBlue)
    instructions = ["INSTRUCTIONS:",
                    "> For each question you will be provided 15 seconds to answer.",
                    "> Answer right give you +1 points",
                    "> Answer wrong and you will get -1 point.",
                    "> The fastest player that get the right answer will the M+1 points ",
                    "(M is the total of points other player lose)",
                    "> If you answer wrong 3 time, game will be over",
                    "> If a player get to the final, the race will end",
                    "GOOD LUCK TO ALL!"]

    partitions = 2 * len(instructions)
    for i, line in enumerate(instructions):
        render_line = instruction_font.render(line, True, whiteBlue)
        question_rect = render_line.get_rect(center=(int(SCREEN_WIDTH / 2),
                                                     (2 * i + 1) * int(SCREEN_HEIGHT / partitions)))
        screen.blit(render_line, question_rect)


def render_game_scene():
    global notice, answer, question, score, rank
    screen.fill(darkerBlue)

    # render question
    render_question = question_font.render(question, True, whiteBlue)
    question_rect = render_question.get_rect(center=(int(SCREEN_WIDTH / 2),
                                                     int(SCREEN_HEIGHT / 6)))
    screen.blit(render_question, question_rect)

    # render life
    render_life = font.render("Life: " + life, True, whiteRed)
    life_rect = render_life.get_rect(center=(int(SCREEN_WIDTH / 2),
                                             int(SCREEN_HEIGHT / 6 + 140)))
    screen.blit(render_life, life_rect)

    # answer box
    # (left, top) (width, height)
    answer_box = pg.Rect((0, 0), (300, 1))
    answer_box.center = (int(SCREEN_WIDTH / 2), 3 * int(SCREEN_HEIGHT / 6) + 80)
    pg.draw.rect(screen, whiteBlue, answer_box)

    # answer
    render_answer = font.render(answer, True, whiteBlue)
    answer_rect = render_answer.get_rect(center=(int(SCREEN_WIDTH / 2),
                                                 3 * int(SCREEN_HEIGHT / 6)))
    screen.blit(render_answer, answer_rect)

    # result
    render_result = font.render("Result: " + result, True, orange)
    result_rect = render_result.get_rect(center=(int(SCREEN_WIDTH / 2),
                                                 3 * int(SCREEN_HEIGHT / 6) + 120))
    screen.blit(render_result, result_rect)

    # instruction
    render_instruction = font.render('Press Space to Answer', True, whiteBlue)
    instruction_rect = render_instruction.get_rect(center=(int(SCREEN_WIDTH / 2),
                                                           5 * int(SCREEN_HEIGHT / 6)))
    screen.blit(render_instruction, instruction_rect)

    # Score
    render_score = font.render('Score: ' + str(score) + f"/{race_length}", True, whiteBlue)
    score_rect = render_score.get_rect(center=(int(SCREEN_WIDTH / 2),
                                               int(SCREEN_HEIGHT / 6) + 70))
    screen.blit(render_score, score_rect)

    # Rank
    render_rank = font.render(rank, True, whiteRed, orange)
    rank_rect = render_rank.get_rect(center=(int(SCREEN_WIDTH / 2),
                                             3 * int(SCREEN_HEIGHT / 6) + 120))
    screen.blit(render_rank, rank_rect)


def render_gameover_scene():
    screen.fill(darkerBlue)
    render_end = over_font.render('Game Over', True, lighterBlue)
    end_rect = render_end.get_rect(center=(int(0.5 * SCREEN_WIDTH),
                                           int(0.5 * SCREEN_HEIGHT)))
    screen.blit(render_end, end_rect)


def render_victory_scene():
    screen.fill(orange)
    render_end = over_font.render('Victory', True, whiteRed)
    end_rect = render_end.get_rect(center=(int(0.5 * SCREEN_WIDTH),
                                           int(0.5 * SCREEN_HEIGHT)))
    screen.blit(render_end, end_rect)


# setup socket and port
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setblocking(False)
client.settimeout(60)
try:
    client.connect((Host, Port))
except:
    print("CAN'T CONNECT TO SERVER!")
    sys.exit()


def update_nickname(_nickname, event):
    if len(_nickname) >= 10:
        return _nickname
    if event.mod == pg.KMOD_NONE or event.mod == 4096:
        if (pg.K_a <= event.key <= pg.K_z) or \
                (pg.K_0 <= event.key <= pg.K_9):
            _nickname += event.unicode
    elif event.mod & pg.KMOD_LSHIFT or event.mod & pg.KMOD_CAPS:
        if pg.K_a <= event.key <= pg.K_z:
            _nickname += event.unicode.upper()
        elif event.key == pg.K_MINUS:
            _nickname += "_"
        else:
            pass
    return _nickname


def update_answer(_answer, event):
    if event.mod == pg.KMOD_NONE or event.mod == 4096:
        if pg.K_0 <= event.key <= pg.K_9 or event.key == pg.K_MINUS:
            _answer += event.unicode
    return _answer


def handle_login_state():
    global game_state, nickname, notice

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                nickname = nickname[:-1]
                if nickname == '':
                    notice = '!~ Please input your name ~!'
            else:
                notice = ''
                nickname = update_nickname(nickname, event)

            if event.key == pg.K_SPACE:
                if isValidName(nickname):
                    print(nickname)
                    print("Nickname is valid!")
                    try:
                        client.send(bytes(nickname, 'utf-8'))
                    except:
                        client.close()
                else:
                    if nickname == '':
                        notice = '!~ Please fill in your nickname ~!'


def handle_starting_state():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()


def handle_started_state():
    global answer
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                answer = answer[:-1]
            elif event.key == pg.K_SPACE:
                if len(answer) == 0:
                    answer = "None"
                print(answer)
                try:
                    client.send(bytes(answer, 'utf-8'))
                except:
                    client.close()
            else:
                answer = update_answer(answer, event)


def listening_to_server():
    global client, notice, game_state, nickname, question, answer, race_length, score, result, life, rank

    while True:
        message = receive_message(client)
        print(message)
        if not message:
            print("DISCONNECTED")
            sys.exit()
        else:
            if message == "Name already taken":
                notice = "Name already taken. Please choose another one!!!"
                print("Name already taken. Please choose another one!!!")
                nickname = ""
            elif "start game" in message:
                print("game_state: starting", )
                continue
            elif len(message) > 2:
                if "Q|" in message:
                    answer = ''
                    result = ''
                    rank = ''
                    question = str(message.split("Q|")[-1])
                    game_state = GameState.STARTED
                elif "RL|" in message:
                    race_length = int(message.split("RL|")[-1])
                    game_state = GameState.STARTING
                elif "A|" in message:
                    result = message.split("A|")[-1]
                elif "MS|" in message:
                    temp = message.split("MS|")[-1].split("|L|")
                    score = temp[0]
                    life = temp[1]
                elif "S|" in message:
                    score = int(message.split("S|")[-1])
                elif "Top" in message:
                    rank = 'You are NO.1. No one is better than you!'
                elif "P|" in message:
                    temp = message.split("P|")[-1].split("|B|")
                    rank = f'You are NO.{temp[0]}. Behind {temp[1]}'
                elif "Win" in message:
                    game_state = GameState.WIN
                elif "Gameover" in message:
                    game_state = GameState.OVER


listen_thread = start_new_thread(listening_to_server, ())

while True:
    if game_state == GameState.LOGIN:
        handle_login_state()
        render_login_scene()
    elif game_state == GameState.STARTING:
        render_waiting_scene()
        handle_starting_state()
    elif game_state == GameState.STARTED:
        render_game_scene()
        handle_started_state()
    elif game_state == GameState.OVER:
        render_gameover_scene()
        handle_starting_state()
    elif game_state == GameState.WIN:
        render_victory_scene()
        handle_starting_state()
    pg.display.update()
