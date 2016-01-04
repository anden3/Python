import pickle
import sys
from statistics import median

import pygame
import requests

from math import floor

screen = None
menu_visible = False
textbox_visible = False

width = 0
height = 0
scale = 0
delay = 0

buttons = {}
textboxes = {}
active_cells = set()


class Button:
    def __init__(self, text):
        self.name = text
        self.font = pygame.font.Font(None, 50)
        self.text = self.font.render(text, 1, (0, 0, 0))

        self.w = self.font.size(text)[0] + 10
        self.h = self.font.size(text)[1] + 10

        self.x = (width * scale - self.w) / 2
        self.y = len(buttons) * 70 + 10

        self.rect = (self.x, self.y, self.w, self.h)

    def draw(self):
        screen.fill((160, 160, 160), rect=self.rect)
        screen.blit(self.text, (self.x + 5, self.y + 5))


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


def new_array():
    return [0] * (height * width)


def toggle_cell(x, y, state):
    rect = (x * scale, y * scale, scale, scale)

    if state:
        screen.fill((0, 0, 0), rect=rect)
    else:
        screen.fill((255, 255, 255), rect=rect)

    pygame.display.update(rect)


def click_cell(pos, board, button):
    cell_x = floor(pos[0] / scale)
    cell_y = floor(pos[1] / scale)
    index = cell_y * height + cell_x

    if board[index] == 1 and button == 3:
        board[index] = 0
        toggle_cell(cell_x, cell_y, 0)
    elif board[index] == 0 and button == 1:
        board[index] = 1
        toggle_cell(cell_x, cell_y, 1)


def cell_check(board, rescan=False):
    new_board = new_array()

    if rescan or not active_cells:
        active_cells.clear()

        for i in range(width * height):
            x = i % width
            y = floor(i / height)

            if x == 0:
                x_vals = [width - 1, 0, 1]
            elif x == width - 1:
                x_vals = [x - 1, x, 0]
            else:
                x_vals = [x - 1, x, x + 1]

            if y == 0:
                y_vals = [height - 1, 0, 1]
            elif y == height - 1:
                y_vals = [y - 1, y, 0]
            else:
                y_vals = [y - 1, y, y + 1]

            field_sum = sum([board[a * width + b] for a in y_vals for b in x_vals])

            if field_sum == 3 or (field_sum == 4 and board[i] == 1):
                active_cells.add(i)
            '''
            elif field_sum != 4:
                new_board[i] = 0
            else:
                new_board[i] = board[i]
            '''

        return board
    else:
        for i in active_cells.copy():
            x = i % width
            y = floor(i / height)

            if x == 0:
                x_neighbors = [width - 1, 0, 1]
            elif x == width - 1:
                x_neighbors = [x - 1, x, 0]
            else:
                x_neighbors = [x - 1, x, x + 1]

            if y == 0:
                y_neighbors = [height - 1, 0, 1]
            elif y == height - 1:
                y_neighbors = [y - 1, y, 0]
            else:
                y_neighbors = [y - 1, y, y + 1]

            for cx in x_neighbors:
                for cy in y_neighbors:
                    index = cy * width + cx

                    if cx == 0:
                        x_vals = [width - 1, 0, 1]
                    elif cx == width - 1:
                        x_vals = [cx - 1, cx, 0]
                    else:
                        x_vals = [cx - 1, cx, cx + 1]

                    if cy == 0:
                        y_vals = [height - 1, 0, 1]
                    elif cy == height - 1:
                        y_vals = [cy - 1, cy, 0]
                    else:
                        y_vals = [cy - 1, cy, cy + 1]

                    field_sum = sum([board[a * width + b] for a in y_vals for b in x_vals])

                    if field_sum == 3:
                        new_board[index] = 1

                        if index not in active_cells:
                            active_cells.add(index)

                    elif field_sum != 4:
                        active_cells.discard(index)
                    else:
                        new_board[index] = board[index]
        return new_board


def draw_board():
    screen.fill((255, 255, 255))

    for i in active_cells:
        rect = ((i % width) * scale, floor(i / height) * scale, scale, scale)
        screen.fill((0, 0, 0), rect=rect)

    pygame.display.flip()


def toggle_menu():
    global menu_visible

    if menu_visible:
        menu_visible = False
        draw_board()
    else:
        menu_visible = True
        screen.fill((255, 255, 255))
        [button.draw() for button in buttons.values()]
        pygame.display.flip()


def save_game(board):
    pickle.dump(board, open('save_file.txt', 'wb'))


def load_game():
    global menu_visible
    menu_visible = False

    game(0, load_board=pickle.load(open('save_file.txt', 'rb')), rescan=True)


def load_external(path=None):
    if path is None:
        global textbox_visible
        textbox_visible = True

        screen.fill((255, 255, 255))
        pygame.display.flip()

        textboxes['path'] = Textbox(50)
        textboxes['path'].draw()

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
        board[y_vals[i] * width + x_vals[i]] = 1

    game(0, load_board=board, rescan=True)


def parse_life_1_06(pattern):
    lines = repr(pattern).split(r'\r\n')

    x_vals = []
    y_vals = []
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
        board[y_vals[i] * width + x_vals[i]] = 1

    game(0, load_board=board, rescan=True)


def parse_plaintext(pattern):
    lines = repr(pattern).split(r'\r\n')

    x_vals = []
    y_vals = []
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
        board[y_vals[i] * width + x_vals[i]] = 1

    game(0, load_board=board, rescan=True)


def parse_rle(pattern):
    global width, height
    lines = repr(pattern).split(r'\r\n')

    x_vals = []
    y_vals = []
    cell_block = []

    cell_block_start = [i for i in range(len(lines)) if lines[i][0:1] != '#' and lines[i][0:2] != "'#"][0]
    parameters = lines[cell_block_start].split(',')

    w = int(parameters[0][4:])
    h = int(parameters[1][4:])

    if w > width:
        width = w
    if h > height:
        height = h

    board = new_array()

    if len(parameters) > 2:
        has_normal_rules = True if parameters[2][8:].lower() == 'b3/s23' else False

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

    w_padding = (width - len(set(x_vals))) // 2
    h_padding = (height - len(set(y_vals))) // 2

    if min(x_vals) < w_padding:
        diff = (min(x_vals) * -1) + w_padding
        for x in range(len(x_vals.copy())):
            x_vals[x] += diff

    if min(y_vals) < h_padding:
        diff = (min(y_vals) * -1) + h_padding
        for y in range(len(y_vals.copy())):
            y_vals[y] += diff

    for i in range(len(x_vals)):
        board[y_vals[i] * width + x_vals[i]] = 1

    game(0, load_board=board, rescan=True)


def game(steps, load_board=None, rescan=False):
    global menu_visible, textbox_visible
    menu_visible = False
    textbox_visible = False

    if load_board is not None:
        board = cell_check(load_board, rescan=rescan)
    else:
        board = cell_check(new_array())

    current_step = 0
    start_generations = False
    mouse_down = False
    ctrl_pressed = False
    mouse_button_down = 0
    old_mouse_pos = (-1, -1)
    path_string = ""

    last = pygame.time.get_ticks()

    draw_board()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button_down = event.button

                if not menu_visible:
                    mouse_down = True
                else:
                    mouse_pos = pygame.mouse.get_pos()

                    for button in buttons.values():
                        if abs((button.x + button.w / 2) - mouse_pos[0]) < button.w / 2 and abs((button.y + button.h / 2) - mouse_pos[1]) < button.h / 2:
                            if button.name.lower() == "resume":
                                toggle_menu()
                                break

                            elif button.name.lower() == "save":
                                save_game(board)
                                break

                            elif button.name.lower() == "load":
                                load_game()
                                break

                            elif button.name.lower() == "load external":
                                load_external()
                                break

                            elif button.name.lower() == "quit":
                                pygame.quit()
                                sys.exit()

            elif event.type == pygame.MOUSEBUTTONUP:
                if not menu_visible:
                    mouse_down = False
                    old_mouse_pos = (-1, -1)

            elif textbox_visible and event.type == pygame.KEYDOWN:
                if event.key != 13:
                    if event.key == 306:
                        ctrl_pressed = True
                    elif event.key == 8:
                        path_string = path_string[0:-1]
                    else:
                        if ctrl_pressed and event.key == 118:
                            path_string = pygame.scrap.get('text/plain')[:-1].decode('UTF-8')
                        else:
                            path_string += event.unicode

                    textboxes['path'].update(path_string)

                elif len(path_string) > 1:
                    load_external(path_string)

            elif event.type == pygame.KEYUP:
                if event.key == 306:  # Ctrl
                    ctrl_pressed = False

                elif event.key == 27:  # Escape
                    toggle_menu()

                if not textbox_visible:
                    if event.key == 32:  # Space
                        start_generations = True

                    elif event.key == 114:  # R
                        game(steps, load_board=new_array())

                    elif 48 <= event.key <= 57:  # 0-9
                        global delay

                        if event.key == 48:
                            delay = 0

                        elif event.key == 49:
                            delay = 1000

                        elif event.key == 50:
                            delay = 500

                        elif event.key == 51:
                            delay = 250

                        elif event.key == 52:
                            delay = 100

                        elif event.key == 53:
                            delay = 50

                        elif event.key == 54:
                            delay = 25

                        elif event.key == 55:
                            delay = 10

                        elif event.key == 56:
                            delay = 5

                        elif event.key == 57:
                            delay = 0
        if mouse_down:
            mouse_pos = pygame.mouse.get_pos()

            if floor(mouse_pos[0] / scale) != floor(old_mouse_pos[0] / scale) or floor(mouse_pos[1] / scale) != floor(old_mouse_pos[1] / scale):
                old_mouse_pos = mouse_pos
                click_cell(mouse_pos, board, mouse_button_down)

        now = pygame.time.get_ticks()

        if start_generations and not menu_visible:
            if now - last >= delay:
                if steps == 0 or current_step < steps:
                    current_step += 1
                    last = now

                    board = cell_check(board)
                    draw_board()


def start(w, h, steps, d, s):
    pygame.init()

    global width, height, delay, scale
    width = w
    height = h
    delay = d
    scale = s

    buttons['resume'] = Button("Resume")
    buttons['save'] = Button("Save")
    buttons['load'] = Button("Load")
    buttons['load_ext'] = Button("Load external")
    buttons['quit'] = Button("Quit")

    global screen
    screen = pygame.display.set_mode((width * scale, height * scale))
    screen.fill((255, 255, 255))

    pygame.scrap.init()

    game(steps)

start(100, 100, 0, 0, 10)
