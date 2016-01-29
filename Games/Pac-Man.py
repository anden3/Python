import sys

import pyglet
import pyglet.gl as gl
from pyglet.window import key

from math import floor

width = 0
height = 0
scale = 0

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

board_width = 26
board_height = 8

dots = set()
walls = set()

board = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
]

wall_vertices = {
    'left': [(9, 0, 2, 20)],
    'right': [(9, 0, 2, 20)],
    'top': [(0, 9, 20, 2)],
    'bottom': [(0, 9, 20, 2)],
    'upleft': [(10, 0, 2, 6), (11, 7, 1, 1), (12, 8, 1, 1), (13, 9, 1, 1), (14, 10, 3, 2)]
}


def parse_board():
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == 1 or board[y][x] == 2:
                dots.add((x, y, board[y][x] == 2))
            else:
                if y > 0 and board[y - 1][x] == 0:  # Bottom
                    if y < board_height - 1 and board[y + 1][x] == 0:  # Top
                        if x > 0 and board[y][x - 1] == 0:  # Left
                            if x == board_width - 1 or board[y][x + 1] != 0:
                                walls.add((x, y, 'left'))
                        elif x < board_width - 1 and board[y][x + 1] == 0:  # Right
                            if x == 0 or board[y][x - 1] != 0:
                                walls.add((x, y, 'right'))


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


def draw_sub_rect(x, y, sx, sy, sw, sh, c):
    r, g, b = c

    batch.add(4, gl.GL_QUADS, None,
              ('v2f', ((x * scale) + sx, (y * scale) + sy,
                       (x * scale) + sx + sw, (y * scale) + sy,
                       (x * scale) + sx + sw, (y * scale) + sy + sh,
                       (x * scale) + sx, (y * scale) + sy + sh)),
              ('c3f', (r, g, b, r, g, b, r, g, b, r, g, b)))


def draw_board():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    for x, y, direction in walls:
        [draw_sub_rect(x, height - y - 1, sx, sy, sw, sh, (0.0, 0.0, 1.0)) for sx, sy, sw, sh in wall_vertices[direction]]

    for x, y, big in dots:
        if big:
            draw_sub_rect(x, height - y - 1, 6, 6, 8, 8, (1.0, 1.0, 0.0))
        else:
            draw_sub_rect(x, height - y - 1, 8, 8, 4, 4, (1.0, 1.0, 0.0))

    batch.draw()


@window.event
def on_key_press(symbol, modifers):
    if symbol == key.Q:
        sys.exit()


@window.event
def on_draw():
    window.clear()
    draw_board()


def start(w=1280, h=720, s=20):
    gl.glClearColor(0.0, 0.0, 0.0, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    window.set_size(w, h)

    global width, height, scale
    scale = s
    width = floor(w / scale)
    height = floor(h / scale)

    parse_board()

    pyglet.app.run()

start()
