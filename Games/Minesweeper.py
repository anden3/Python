import pickle
import sys
from random import random

import pyglet
import pyglet.gl as gl
from pyglet.window import key

from math import floor

sys.setrecursionlimit(100000)

width = 0
height = 0
scale = 0
mine_num = 0

first_click = True
game_running = True

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

board = []
mines = set()
board_visibility = set()
flags = set()

number_vertices = {
    1: [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (1, 3)],
    2: [(3, 0), (2, 0), (1, 0), (1, 1), (2, 1.5), (3, 2), (3, 3), (3, 4), (2, 4), (1, 4), (1, 3)],
    3: [(1, 0), (2, 0), (3, 0), (3, 1), (3, 2), (2, 2), (1, 2), (3, 3), (3, 4), (2, 4), (1, 4)],
    4: [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (2, 2), (1, 2), (1, 3), (1, 4)],
    5: [(1, 0), (2, 0), (3, 0), (3, 1), (3, 2), (2, 2), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4)],
    6: [(1, 0), (2, 0), (3, 0), (3, 1), (3, 2), (2, 2), (1, 2), (1, 1), (1, 3), (1, 4), (2, 4), (3, 4)],
    7: [(1, 4), (2, 4), (3, 4), (3, 3), (2.33, 2), (2, 1), (1.66, 0)],
    8: [(1, 0), (2, 0), (3, 0), (1, 1), (3, 1), (1, 2), (2, 2), (3, 2), (1, 3), (3, 3), (1, 4), (2, 4), (3, 4)],
    9: [(1, 0), (2, 0), (3, 0), (3, 1), (1, 2), (2, 2), (3, 2), (1, 3), (3, 3), (1, 4), (2, 4), (3, 4)]
}

number_colors = {
    1: (0.0, 1.0, 0.0),  # Blue
    2: (0.0, 0.0, 1.0),  # Green
    3: (1.0, 0.0, 0.0),  # Red
    4: (0.0, 0.5, 0.0),  # Dark blue
    5: (0.647, 0.1647, 0.1647),  # Brown
    6: (0.0, 1.0, 1.0),  # Cyan
    7: (0.0, 0.0, 0.0),  # Black
    8: (0.6, 0.6, 0.6)   # Grey
}


def draw_rect(x, y, c):
    r, g, b = c
    padding_lt = 1
    padding_rb = 1

    batch.add(4, gl.GL_QUADS, None,
              ('v2f', (x * scale + padding_lt, y * scale + padding_lt,
                       x * scale + scale - padding_rb, y * scale + padding_lt,
                       x * scale + scale - padding_rb, y * scale + scale - padding_rb,
                       x * scale + padding_lt, y * scale + scale - padding_rb)),
              ('c3f', (r, g, b, r, g, b, r, g, b, r, g, b)))


def draw_sub_rect(x, y, sx, sy, c):
    r, g, b = c

    padding = 2
    sw = floor((scale - padding) / 5)

    batch.add(4, gl.GL_QUADS, None,
              ('v2f', ((x * scale + padding) + (sx * sw), (y * scale + padding) + (sy * sw),
                       (x * scale + padding) + (sx * sw) + sw, (y * scale + padding) + (sy * sw),
                       (x * scale + padding) + (sx * sw) + sw, (y * scale + padding) + (sy * sw) + sw,
                       (x * scale + padding) + (sx * sw), (y * scale + padding) + (sy * sw) + sw)),
              ('c3f', (r, g, b, r, g, b, r, g, b, r, g, b)))


def draw_number(x, y, num):
    if 1 <= num <= 9:
        [draw_sub_rect(x, y, sx, sy, number_colors[num]) for sx, sy in number_vertices[num]]
    else:
        return


def save_game():
    save_data = [width, height, scale, board, mines, board_visibility, flags]
    pickle.dump(save_data, open('minesweeper_save.txt', 'wb'))


def load_game():
    save_data = pickle.load(open('minesweeper_save.txt', 'rb'))

    global batch
    batch = pyglet.graphics.Batch()

    global width, height, scale, board, mines, board_visibility, flags
    width = save_data[0]
    height = save_data[1]
    scale = save_data[2]
    board = save_data[3]
    mines = save_data[4]
    board_visibility = save_data[5]
    flags = save_data[6]

    window.dispatch_event('on_draw')


def reset_game():
    global first_click, game_running, batch
    first_click = True
    game_running = True

    batch = pyglet.graphics.Batch()

    mines.clear()
    board_visibility.clear()
    flags.clear()

    new_board()
    add_mines()
    add_numbers()

    window.dispatch_event('on_draw')


def game_over():
    for x, y in mines:
        [draw_sub_rect(x, y, sx, sy, (0.0, 0.0, 0.0)) for sx, sy in [(1, 0), (3, 0), (1.5, 1), (2.5, 1), (2, 2), (1.5, 3), (2.5, 3), (1, 4), (3, 4)]]


def new_board():
    global board
    board = [[0 for _ in range(width)] for _ in range(height)]


def add_mines():
    probability = float(mine_num / (height * width))
    print("Mine probability: " + str(round(probability * 100, 2)) + "%.")

    [mines.add((x, y)) for x in range(width) for y in range(height) if random() < probability]


def add_numbers():
    for y in range(height):
        if y == 0:
            y_vals = [0, 1]
        elif y == width - 1:
            y_vals = [y - 1, y]
        else:
            y_vals = [y - 1, y, y + 1]

        for x in range(width):
            if x == 0:
                x_vals = [0, 1]
            elif x == width - 1:
                x_vals = [x - 1, x]
            else:
                x_vals = [x - 1, x, x + 1]

            board[y][x] = sum([1 for cx in x_vals for cy in y_vals if (cx, cy) in mines])


def board_clear(x, y):
    if not (0 <= x <= width - 1) or not(0 <= y <= height - 1):
        return

    if (x, y) in board_visibility:
        return

    board_visibility.add((x, y))

    if board[y][x] > 0:
        return
    else:
        board_clear(x - 1, y)
        board_clear(x + 1, y)
        board_clear(x, y - 1)
        board_clear(x, y + 1)


def draw_board():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    for x, y in board_visibility:
        draw_rect(x, y, (1.0, 1.0, 1.0))
        draw_number(x, y, board[y][x])

    [draw_rect(x, y, (1.0, 0.0, 0.0)) for x, y in flags]

    batch.draw()


@window.event
def on_key_press(symbol, modifers):
    if symbol == key.Q:
        sys.exit()
    elif symbol == key.S:
        save_game()
    elif symbol == key.L:
        load_game()
    elif symbol == key.R:
        reset_game()


@window.event
def on_mouse_press(x, y, buttons, modifers):
    global game_running

    cell_x = floor(x / scale)
    cell_y = floor(y / scale)

    if game_running and (cell_x, cell_y) not in board_visibility:
        if buttons == 1 and (cell_x, cell_y) not in flags:
            global first_click

            if (cell_x, cell_y) not in mines:
                first_click = False

                if board[cell_y][cell_x] == 0:
                    board_clear(cell_x, cell_y)
                else:
                    board_visibility.add((cell_x, cell_y))
            elif first_click:
                first_click = False

                mines.discard((cell_x, cell_y))

                if (0, 0) not in mines:
                    mines.add((0, 0))
                elif (width - 1, 0) not in mines:
                    mines.add((width - 1, 0))
                elif (width - 1, height - 1) not in mines:
                    mines.add((width - 1, height - 1))
                else:
                    mines.add((0, height - 1))

                new_board()
                add_numbers()

                if board[cell_y][cell_x] == 0:
                    board_clear(cell_x, cell_y)
                else:
                    board_visibility.add((cell_x, cell_y))

            else:
                print("Game over!")
                game_running = False
                game_over()

        elif buttons == 4:
            if (cell_x, cell_y) in flags:
                flags.discard((cell_x, cell_y))
                draw_rect(cell_x, cell_y, (0.6, 0.6, 0.6))
            else:
                flags.add((cell_x, cell_y))

                if flags == mines:
                    print("You have won!")
                    game_running = False


@window.event
def on_draw():
    window.clear()
    draw_board()


def start(w=1280, h=720, s=20, m=300):
    gl.glClearColor(0.6, 0.6, 0.6, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    window.set_size(w, h)

    global width, height, scale, mine_num
    scale = s
    width = floor(w / scale)
    height = floor(h / scale)
    mine_num = m

    new_board()
    add_mines()
    add_numbers()

    pyglet.app.run()

start()
