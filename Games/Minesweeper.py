from random import random

width = 0
height = 0
mines = 0

board = []
board_visibility = []


def new_board():
    global board
    board = [[0 for _ in range(width)] for _ in range(height)]


def create_board():
    for y in range(height):
        for x in range(width):
            board[y][x] = round(random())

    print(board)


def start(w=10, h=10):
    global width, height
    width, height = w, h

    new_board()
    create_board()

start()
