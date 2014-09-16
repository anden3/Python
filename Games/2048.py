import math
import random
import sys

# noinspection PyPep8
board = [["_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_"]]
score = [0]


def print_board():
    for x in board:
        print(" ".join(x))


def random_placer():
    x = math.floor(random.randint(0, 5))
    y = math.floor(random.randint(0, 5))
    n = math.floor(random.randint(0, 1))
    if n == 0:
        rand_num = "2"
    else:
        rand_num = "4"
    if board[x][y] == "_":
        board[x][y] = rand_num
        print("Score: " + str(score[0]))
        print_board()
    else:
        random_placer()


def winning():
    for x in board:
        if "2048" in x:
            print("You have won!")
            print("Your score is " + str(score[0]) + "!")
            sys.exit()


def gameover():
    full_rows = 0
    for x in board:
        if "_" not in x:
            full_rows += 1
    if full_rows == 6:
        print("Game Over!")
        print("Your score is " + str(score[0]) + "!")
        sys.exit()


def player_control(direction):
    if direction == "up" or direction == "w":
        for _ in board:
            for x in range(5, 0, -1):
                for y in range(5, -1, -1):
                    if board[x][y] != "_" and board[x - 1][y] == "_":
                        board[x - 1][y] = board[x][y]
                        board[x][y] = "_"
                    elif board[x][y] != "_" and board[x - 1][y] == board[x][y]:
                        board[x - 1][y] = str(int(board[x][y]) + int(board[x - 1][y]))
                        score[0] += int(board[x - 1][y])
                        board[x][y] = "_"
    elif direction == "down" or direction == "s":
        for _ in board:
            for x in range(0, 5):
                for y in range(0, 6):
                    if board[x][y] != "_" and board[x + 1][y] == "_":
                        board[x + 1][y] = board[x][y]
                        board[x][y] = "_"
                    elif board[x][y] != "_" and board[x + 1][y] == board[x][y]:
                        board[x + 1][y] = str(int(board[x][y]) + int(board[x + 1][y]))
                        score[0] += int(board[x + 1][y])
                        board[x][y] = "_"
    elif direction == "left" or direction == "a":
        for _ in board:
            for y in range(5, 0, -1):
                for x in range(0, 6):
                    if board[x][y] != "_" and board[x][y - 1] == "_":
                        board[x][y - 1] = board[x][y]
                        board[x][y] = "_"
                    elif board[x][y] != "_" and board[x][y - 1] == board[x][y]:
                        board[x][y - 1] = str(int(board[x][y]) + int(board[x][y - 1]))
                        score[0] += int(board[x][y - 1])
                        board[x][y] = "_"
    elif direction == "right" or direction == "d":
        for _ in board:
            for y in range(0, 5):
                for x in range(0, 6):
                    if board[x][y] != "_" and board[x][y + 1] == "_":
                        board[x][y + 1] = board[x][y]
                        board[x][y] = "_"
                    elif board[x][y] != "_" and board[x][y + 1] == board[x][y]:
                        board[x][y + 1] = str(int(board[x][y]) + int(board[x][y + 1]))
                        score[0] += int(board[x][y + 1])
                        board[x][y] = "_"
    elif direction == "exit" or direction == "x":
        if input("Exit? Y/N: ") == "y":
            print("Your score is " + str(score[0]) + "!")
            sys.exit()
        else:
            player_control(input("Direction: "))
    else:
        print_board()
        player_control(input("Invalid input, please try again: "))
    next_move()


def next_move():
    winning()
    gameover()
    random_placer()
    player_control(str(input("Direction: ")))

next_move()