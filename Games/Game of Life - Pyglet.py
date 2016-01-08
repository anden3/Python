import pickle
import sys
from itertools import product
from random import random
from statistics import median
from time import clock

import numpy as np
import pyglet
import pyperclip
import requests
from pyglet.gl import *
from pyglet.window import key

from math import floor

window = pyglet.window.Window(style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)

menu_visible = False
textbox_visible = False
loop_running = False

old_cell_x = -1
old_cell_y = -1
old_mouse_button = 0

width = 0
height = 0
scale = 0
delay = 0

path_string = ""

ui_buttons = {}
textboxes = {}
active_cells = set()
board = []
neighbors = []

ui_batch = pyglet.graphics.Batch()


'''
class Textbox:
    def __init__(self, y):
        self.font = pygame.font.Font(None, 20)

        self.x = (width * scale - 300) / 2
        self.y = y

        self.w = 300
        self.h = 30

        self.text = None

    def draw(self):
        screen.fill((200, 200, 200), rect=(self.x, self.y, self.w, self.h))
        pygame.display.update((self.x, self.y, self.w, self.h))

    def update(self, text):
        if self.font.size(text)[0] > 290:
            self.w = self.font.size(text)[0] + 10
            self.x = (width * scale - self.w) / 2

        self.text = self.font.render(text, 1, (0, 0, 0))

        screen.fill((200, 200, 200), rect=(self.x, self.y, self.w, self.h))
        screen.blit(self.text, (self.x + 5, self.y + 5))

        pygame.display.update((self.x, self.y, self.w, self.h))
'''


def draw_rect(x, y, c):
    r, g, b = c

    glBegin(GL_QUADS)
    glColor3f(r, g, b)

    glVertex2f(x * scale, y * scale)
    glVertex2f(x * scale + scale, y * scale)
    glVertex2f(x * scale + scale, y * scale + scale)
    glVertex2f(x * scale, y * scale + scale)
    glEnd()


def new_array(rand=False):
    if rand:
        # return [[1 if random() > 0.5 else 0 for _ in range(width)] for _ in range(height)]
        return np.array([[1 if random() > 0.5 else 0 for _ in range(width)] for _ in range(height)])
    else:
        # return [[0 for _ in range(width)] for _ in range(height)]
        return np.zeros((height, width))


def cell_check(rescan=False):
    new_board = new_array()

    if rescan or not active_cells:
        global neighbors
        neighbors = np.zeros((height, width, 2, 3), dtype=int)

        for y in range(height):
            if y == 0:
                y_vals = [height - 1, 0, 1]
            elif y >= height - 1:
                y_vals = [y - 1, y, 0]
            else:
                y_vals = [y - 1, y, y + 1]

            for x in range(width):
                field_sum = 0

                if x == 0:
                    x_vals = [width - 1, 0, 1]
                elif x >= width - 1:
                    x_vals = [x - 1, x, 0]
                else:
                    x_vals = [x - 1, x, x + 1]

                for i in range(3):
                    neighbors[y][x][0][i] = x_vals[i]
                    neighbors[y][x][1][i] = y_vals[i]

                for a in y_vals:
                    for b in x_vals:
                        field_sum += board[a][b]

                if field_sum == 3 or (field_sum == 4 and board[y][x] == 1):
                    active_cells.add((x, y))

        return board
    else:
        for x, y in active_cells.copy():
            for cx, cy in product(neighbors[y][x][0], neighbors[y][x][1]):
                field_sum = 0

                for nx, ny in product(neighbors[cy][cx][0], neighbors[cy][cx][1]):
                    if board[ny][nx] == 1:
                        field_sum += 1

                if field_sum == 3:
                    new_board[cy][cx] = 1

                    if (cx, cy) not in active_cells:
                        active_cells.add((cx, cy))

                elif field_sum != 4:
                    active_cells.discard((cx, cy))
                else:
                    new_board[cy][cx] = board[cy][cx]

        return new_board


def toggle_menu():
    global menu_visible
    menu_visible = not menu_visible


def save_game():
    pickle.dump(board, open('save_file.txt', 'wb'))


def load_game():
    global menu_visible, board
    menu_visible = False
    board = pickle.load(open('save_file.txt', 'rb'))

    game(load_board=True, rescan=True)


def load_external(path=None):
    if path is None:
        global textbox_visible
        textbox_visible = True

        glClear(GL_COLOR_BUFFER_BIT)

        # textboxes['path'] = Textbox(50)
        # textboxes['path'].draw()

    else:
        if path[-4:] == ".lif" or path[-4:] == ".rle" or path[-6:] == ".cells":
            if path[0:4] == "http":
                get_pattern_type(requests.get(path).text)
            else:
                get_pattern_type(open(path, 'r').read())


def get_pattern_type(pattern):
    if pattern[:10] == "#Life 1.05":
        parse_life_1_05(pattern)

    elif pattern[:10] == "#Life 1.06":
        parse_life_1_06(pattern)

    elif pattern[:6] == "!Name:":
        parse_plaintext(pattern)

    elif pattern[:2] == "#N":
        parse_rle(pattern)


def parse_life_1_05(pattern):
    active_cells.clear()

    lines = repr(pattern).split(r'\r\n')

    x_vals = []
    y_vals = []

    global board
    board = new_array()

    cell_block_start = [i for i in range(len(lines)) if '#' not in lines[i]][0]

    has_normal_rules = [True for line in lines if line.lower() == '#n' or line.lower() == '#r 23/3'][0]

    if not has_normal_rules:
        print("This program doesn't support custom rules yet")
        return

    for y in range(cell_block_start, len(lines)):
        for x in range(len(lines[y])):
            if lines[y][x] == "*":
                x_vals.append(x)
                y_vals.append(y)

    w_padding = (width - len(set(x_vals))) // 2
    h_padding = (height - len(set(y_vals))) // 2

    if floor(median(x_vals)) < w_padding:
        diff = (floor(median(x_vals)) * -1) + w_padding
        for x in range(len(x_vals.copy())):
            x_vals[x] += diff

    if floor(median(y_vals)) < h_padding:
        diff = floor((median(y_vals)) * -1) + h_padding
        for y in range(len(y_vals.copy())):
            y_vals[y] += diff

    for i in range(len(x_vals)):
        board[y_vals[i]][x_vals[i]] = 1

    game(load_board=True, rescan=True)


def parse_life_1_06(pattern):
    lines = repr(pattern).split(r'\r\n')

    x_vals = []
    y_vals = []

    global board
    board = new_array()

    for line in lines[1::]:
        if len(line) > 1:
            x_vals.append(int(line.split()[0]))
            y_vals.append(int(line.split()[1]))

    w_padding = (width - len(set(x_vals))) // 2
    h_padding = (height - len(set(y_vals))) // 2

    if floor(median(x_vals)) < w_padding:
        diff = (floor(median(x_vals)) * -1) + w_padding
        for x in range(len(x_vals.copy())):
            x_vals[x] += diff

    if floor(median(y_vals)) < h_padding:
        diff = floor((median(y_vals)) * -1) + h_padding
        for y in range(len(y_vals.copy())):
            y_vals[y] += diff

    for i in range(len(x_vals)):
        board[y_vals[i]][x_vals[i]] = 1

    game(load_board=True, rescan=True)


def parse_plaintext(pattern):
    lines = repr(pattern).split(r'\r\n')

    x_vals = []
    y_vals = []

    global board
    board = new_array()

    cell_block_start = [i for i in range(len(lines)) if lines[i][0:1] != '!' and lines[i][0:2] != "'!"][0]

    for y in range(cell_block_start, len(lines)):
        for x in range(len(lines[y])):
            if lines[y][x] == "O":
                x_vals.append(x)
                y_vals.append(y)

    w_padding = (width - len(set(x_vals))) // 2
    h_padding = (height - len(set(y_vals))) // 2

    if floor(median(x_vals)) < w_padding:
        diff = (floor(median(x_vals)) * -1) + w_padding
        for x in range(len(x_vals.copy())):
            x_vals[x] += diff

    if floor(median(y_vals)) < h_padding:
        diff = floor((median(y_vals)) * -1) + h_padding
        for y in range(len(y_vals.copy())):
            y_vals[y] += diff

    for i in range(len(x_vals)):
        board[y_vals[i]][x_vals[i]] = 1

    game(load_board=True, rescan=True)


def parse_rle(pattern):
    lines = []

    global width, height
    if '\\r\\n' in repr(pattern):
        lines = repr(pattern).split('\\r\\n')
    elif '\\n' in repr(pattern):
        lines = repr(pattern).split('\\n')

    x_vals = []
    y_vals = []
    cell_block = []

    cell_block_start = [i for i in range(len(lines)) if lines[i][0:1] != '#' and lines[i][0:2] != "'#"][0]
    parameters = lines[cell_block_start].split(',')

    if len(parameters) > 2:
        has_normal_rules = True if parameters[2][8:].lower() == 'b3/s23' or parameters[2][8:].lower() == '23/3' else False

        if not has_normal_rules:
            print("This program doesn't support custom rules yet")
            return

    current_line = []
    last_num = 1
    last_char_num = False

    for line in lines[cell_block_start + 1:]:
        for c in line.strip(" '").replace(' ', ''):
            if c == '$':
                cell_block.append(current_line)
                current_line = []

                if last_char_num:
                    for _ in range(last_num - 1):
                        cell_block.append(['b'])

                last_char_num = False
                last_num = 1
            elif c == '!':
                cell_block.append(current_line)
                break
            else:
                if c.isdigit():
                    if last_char_num:
                        last_num = int(str(last_num) + c)
                    else:
                        last_num = int(c)

                    last_char_num = True
                else:
                    last_char_num = False

                    for _ in range(last_num):
                        current_line.append(c)
                    last_num = 1

    for y in range(len(cell_block)):
        for x in range(len(cell_block[y])):
            if cell_block[y][x] == "o":
                x_vals.append(x)
                y_vals.append(y)

    w = int(parameters[0][4:])
    h = int(parameters[1][4:])

    global scale, board

    if w > width:
        width = w
        w_padding = 0

        if scale * width > 1000:
            scale = round(1000 / width)
    else:
        w_padding = (width - len(set(x_vals))) // 2

    if h > height:
        height = h
        h_padding = 0

        if scale * height > 1000:
            scale = round(1000 / height)
    else:
        h_padding = (height - len(set(y_vals))) // 2

    board = new_array()

    if round(median(x_vals)) < w_padding:
        diff = round(median(x_vals) * -1) + w_padding
        for x in range(len(x_vals.copy())):
            x_vals[x] += diff

    if round(median(y_vals)) < h_padding:
        diff = round(median(y_vals) * -1) + h_padding
        for y in range(len(y_vals.copy())):
            y_vals[y] += diff

    for i in range(len(x_vals)):
        board[y_vals[i]][x_vals[i]] = 1

    game(load_board=True, rescan=True)


def game(load_board=False, rescan=False):
    global menu_visible, textbox_visible, board
    menu_visible = False
    textbox_visible = False

    if load_board:
        board = cell_check(rescan=rescan)
    else:
        board = new_array()

    update()


def update():
    last = 0

    while True:
        now = clock()

        pyglet.clock.tick()
        window.dispatch_events()

        if loop_running and not menu_visible:
            if now - last >= delay:
                global board
                board = cell_check()
                draw_board()


@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.ESCAPE:
        return pyglet.event.EVENT_HANDLED

    if textbox_visible:
        if symbol != key.ENTER:
            global path_string

            if symbol == key.BACKSPACE:
                path_string = path_string[0:-1]
            elif ((modifiers & key.MOD_CTRL) or (modifiers & key.MOD_COMMAND)) and symbol == key.V:
                path_string = pyperclip.paste()
                print(path_string)
            else:
                textboxes['path'].update(path_string)

        elif len(path_string) > 1:
            load_external(path_string)


@window.event
def on_key_release(symbol, modifers):
    if symbol == key.Q:
        sys.exit()

    elif symbol == key.S:
        save_game()

    elif symbol == key.L:
        load_game()

    elif symbol == key.ESCAPE:
        global textbox_visible
        textbox_visible = False
        toggle_menu()

    if not textbox_visible:
        global delay

        if symbol == key.SPACE:
            global loop_running

            if not loop_running:
                loop_running = True
                cell_check(rescan=True)
            else:
                loop_running = False

        elif symbol == key.R:
            active_cells.clear()
            global board
            board = new_array()

            game(load_board=True)

        elif symbol == key._0:
            delay = 0
            # pyglet.clock.unschedule(update)
            # pyglet.clock.schedule(update)

        elif symbol == key._1:
            delay = 1000
            # pyglet.clock.unschedule(update)
            # pyglet.clock.schedule_interval(update, 1000 / 1000)

        elif symbol == key._2:
            delay = 500
            # pyglet.clock.unschedule(update)
            # pyglet.clock.schedule_interval(update, 500 / 1000)

        elif symbol == key._3:
            delay = 250
            # pyglet.clock.unschedule(update)
            # pyglet.clock.schedule_interval(update, 250 / 1000)

        elif symbol == key._4:
            delay = 100
            # pyglet.clock.unschedule(update)
            # pyglet.clock.schedule_interval(update, 100 / 1000)

        elif symbol == key._5:
            delay = 50
            # pyglet.clock.unschedule(update)
            # pyglet.clock.schedule_interval(update, 50 / 1000)

        elif symbol == key._6:
            delay = 25
            # pyglet.clock.unschedule(update)
            # pyglet.clock.schedule_interval(update, 25 / 1000)

        elif symbol == key._7:
            delay = 10
            # pyglet.clock.unschedule(update)
            # pyglet.clock.schedule_interval(update, 10 / 1000)

        elif symbol == key._8:
            delay = 5
            # pyglet.clock.unschedule(update)
            # pyglet.clock.schedule_interval(update, 5 / 1000)

        elif symbol == key._9:
            delay = 1
            # pyglet.clock.unschedule(update)
            # pyglet.clock.schedule_interval(update, 1 / 1000)


@window.event
def on_text(text):
    if textbox_visible:
        global path_string
        path_string += text


@window.event
def on_mouse_press(x, y, buttons, modifers):
    if not menu_visible:
        global old_cell_x, old_cell_y

        cell_x = floor(x / scale)
        cell_y = floor(y / scale)

        if 0 <= cell_x <= (width - 1) and 0 <= cell_y <= (height - 1):
            if cell_x != old_cell_x or cell_y != old_cell_y:
                old_cell_x = cell_x
                old_cell_y = cell_y

                if buttons == 4 and board[cell_y][cell_x] == 1:
                    board[cell_y][cell_x] = 0
                    active_cells.discard((cell_x, cell_y))

                elif buttons == 1 and board[cell_y][cell_x] == 0:
                    board[cell_y][cell_x] = 1
                    active_cells.add((cell_x, cell_y))

        draw_board()
    else:
        for ui_button in ui_buttons.values():
            if abs((ui_button.x + ui_button.w / 2) - x) < ui_button.w / 2 and abs((ui_button.y + ui_button.h / 2) - y) < ui_button.h / 2:
                if ui_button.name.lower() == "resume":
                    toggle_menu()
                    break

                elif ui_button.name.lower() == "save":
                    save_game()
                    break

                elif ui_button.name.lower() == "load":
                    load_game()
                    break

                elif ui_button.name.lower() == "load external":
                    load_external()
                    break

                elif ui_button.name.lower() == "quit":
                    sys.exit()


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if not menu_visible:
        global old_cell_x, old_cell_y

        cell_x = floor(x / scale)
        cell_y = floor(y / scale)

        if 0 <= cell_x <= (width - 1) and 0 <= cell_y <= (height - 1):
            if cell_x != old_cell_x or cell_y != old_cell_y:
                old_cell_x = cell_x
                old_cell_y = cell_y

                if buttons == 4 and board[cell_y][cell_x] == 1:
                    board[cell_y][cell_x] = 0
                    active_cells.discard((cell_x, cell_y))

                elif buttons == 1 and board[cell_y][cell_x] == 0:
                    board[cell_y][cell_x] = 1
                    active_cells.add((cell_x, cell_y))

                draw_board()

            elif buttons != old_mouse_button:
                if buttons == 4 and board[cell_y][cell_x] == 1:
                    board[cell_y][cell_x] = 0
                    active_cells.discard((cell_x, cell_y))

                elif buttons == 1 and board[cell_y][cell_x] == 0:
                    board[cell_y][cell_x] = 1
                    active_cells.add((cell_x, cell_y))


@window.event
def on_mouse_release(x, y, buttons, modifers):
    global old_cell_x, old_cell_y
    old_cell_x = -1
    old_cell_y = -1


def draw_board():
    window.clear()

    if menu_visible:
        ui_batch.draw()
    else:
        for x, y in active_cells:
            draw_rect(x, y, (0.0, 0.0, 0.0))

    window.flip()


@window.event
def on_draw():
    pass


def start(s, w=None, h=None):
    # window.push_handlers(pyglet.window.event.WindowEventLogger())
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    global scale, width, height
    scale = s

    if w is not None and h is not None:
        window.set_size(w, h)

        width = floor(w / scale)
        height = floor(h / scale)
    else:
        window.set_size(width * scale, height * scale)

    ui_buttons['resume'] = pyglet.text.Label('Resume', font_name='Times New Roman', font_size=20, x=window.width // 2, y=len(ui_buttons) * 70 + 10, batch=ui_batch)
    ui_buttons['save'] = pyglet.text.Label('Save', font_name='Times New Roman', font_size=20, x=window.width // 2, y=len(ui_buttons) * 70 + 10, batch=ui_batch)
    ui_buttons['load'] = pyglet.text.Label('Load', font_name='Times New Roman', font_size=20, x=window.width // 2, y=len(ui_buttons) * 70 + 10, batch=ui_batch)
    ui_buttons['load_ext'] = pyglet.text.Label('Load external', font_name='Times New Roman', font_size=20, x=window.width // 2, y=len(ui_buttons) * 70 + 10, batch=ui_batch)
    ui_buttons['quit'] = pyglet.text.Label('Quit', font_name='Times New Roman', font_size=20, x=window.width // 2, y=len(ui_buttons) * 70 + 10, batch=ui_batch)

    game()

    pyglet.app.run()

start(10, 640, 480)
