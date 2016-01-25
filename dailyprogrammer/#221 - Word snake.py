import os
import random
import sys

words = "NICKEL LEDERHOSEN NARCOTRAFFICANTE EAT TO OATS SOUP PAST TELEMARKETER RUST THINGAMAJIG GROSS SALTPETER REISSUE ELEPHANTITIS".split()

height = 100
width = 100
last_direction = 2

possible_dirs = {
    1: [2, 4],
    2: [1, 3],
    3: [2, 4],
    4: [1, 3]
}

pos = [50, 50]
board = []


def create_board():
    global board
    board = [[" " for _ in range(width)] for _ in range(height)]


def return_pos(index, direction):
    if direction == 1:    # Left
        return [pos[0] + index, pos[1]]
    elif direction == 2:  # Down
        return [pos[0], pos[1] + index]
    elif direction == 3:  # Right
        return [pos[0] - index, pos[1]]
    elif direction == 4:  # Up
        return [pos[0], pos[1] - index]


def return_value(index, direction):
    if direction == 1:
        return board[pos[0] + index][pos[1]]
    elif direction == 2:
        return board[pos[0]][pos[1] + index]
    elif direction == 3:
        return board[pos[0] - index][pos[1]]
    elif direction == 4:
        return board[pos[0]][pos[1] - index]


def in_range(length, direction):
    if direction == 1 or direction == 2:
        return pos[direction - 1] < (width - length)
    elif direction == 3 or direction == 4:
        return pos[direction - 3] >= length


def col_detect(length, direction):
    for i in range(1, length + 1):
        if return_value(i, direction) != " ":
            return False
    return True


def return_possible_directions(length):
    directions = [d for d in possible_dirs[last_direction] if in_range(length, d) and col_detect(length, d)]

    if directions:
        return random.choice(directions)
    else:
        os.execv(__file__, sys.argv)


def draw_word(w, direction):
    global pos, last_direction
    last_direction = direction

    for i, c in enumerate(w):
        board_pos = return_pos(i, direction)
        try:
            board[board_pos[0]][board_pos[1]] = c
        except TypeError:
            print(i, direction, pos, board_pos)

    pos = return_pos(len(w) - 1, direction)


def start():
    global board

    create_board()

    for word in words:
        draw_word(word, return_possible_directions(len(word) - 1))

    board = [row for row in board if set(row) != {' '}]

    min_count = 100

    for row in board:
        count = 0
        for cell in row:
            if cell == ' ':
                count += 1
            else:
                break

        if count < min_count:
            min_count = count

    for y in range(len(board)):
        board[y] = list(''.join(board[y]).rstrip())

    for y in range(len(board)):
        del board[y][0:min_count]

    [print(''.join(row)) for row in board]

start()
