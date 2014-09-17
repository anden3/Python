import math
import random
import sys

sys.setrecursionlimit(100000)

board1 = [["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"]]
board2 = [["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_", "_", "_", "_"]]

p1_score = [0]
p2_score = [0]


def print_board():
    for x in board1:
        print(" ".join(x))


def winning():
    if p1_score[0] >= 5:
        print("Player 1 has won!")
        sys.exit()
    elif p2_score[0] >= 5:
        print("Player 2 has won!")
        sys.exit()


def ship_placer(time, board):
    length = math.floor(random.randint(2, 6))
    x = math.floor(random.randint(0, 9))
    y = math.floor(random.randint(0, 9))
    direction = math.floor(random.randint(0, 1))
    while time < 6:
        if direction == 0:
            if x + length > 9:
                ship_placer(time, board)
            for n in range(x, x + length):
                if board[n][y] != "_":
                    ship_placer(time, board)
            board[x][y] = "A"
            board[x + length - 1][y] = "V"
            if length > 2:
                for n in range(x + 1, x + length - 1):
                    board[n][y] = "I"
            ship_placer(time + 1, board)
        if direction == 1:
            if y + length > 9:
                ship_placer(time, board)
            for n in range(y, y + length):
                if board[x][n] != "_":
                    ship_placer(time, board)
            board[x][y] = "<"
            board[x][y + length - 1] = ">"
            if length > 2:
                for n in range(y + 1, y + length - 1):
                    board[x][n] = "="
            ship_placer(time + 1, board)
    else:
        if board == board1:
            ship_placer(1, board2)
        else:
            player_control()


def player_control():
    winning()
    print("P1 Score: " + str(p1_score[0]))
    print("P2 Score: " + str(p2_score[0]))
    print_board()
    x = int(input("X: "))
    y = int(input("Y: "))
    if x > 9 or y > 9 or x < 0 or y < 0:
        print("Invalid input, please try again")
        player_control()
    if board2[x][y] == "<" or board2[x][y] == "=" or board2[x][y] == ">" or board2[x][y] == "A" or board2[x][y] == "I" or board2[x][y] == "V":
        p1_score[0] += 1
        board2[x][y] = "X"
    elif board2[x][y] == "_":
        board1[x][y] = "O"
    elif board2[x][y] == "X" or board1[x][y] == "O":
        print("Already fired there, please try again")
        player_control()
    ai()


def ai():
    x = math.floor(random.randint(0, 9))
    y = math.floor(random.randint(0, 9))
    if board1[x][y] == "<" or board1[x][y] == "=" or board1[x][y] == ">" or board1[x][y] == "A" or board1[x][y] == "I" or board1[x][y] == "V":
        p2_score[0] += 1
        board1[x][y] = "X"
    elif board1[x][y] == "_":
        board2[x][y] = "O"
    elif board1[x][y] == "X" or board2[x][y] == "O":
        ai()
    player_control()

ship_placer(1, board1)