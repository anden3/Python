import pickle
import sys

import pygame
import requests

from math import floor, sqrt

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
                # new_board[i] = 1
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

    '''
    elif pattern[:4] == "x = ":
        parse_rle(pattern)
    '''


def parse_life_1_05(pattern):
    active_cells.clear()

    lines = repr(pattern).split(r'\r\n')

    normal_rules = False
    cell_block = []
    board = []
    start_x = start_y = 0

    for line in lines:
        if '#' not in line:
            cell_block.append(line)
        elif line[:2] == '#N' or line == '#R 23/3':
            normal_rules = True
        elif line[:2] == '#P':
            start_x = line[3:5].strip()
            start_y = line[6:8].strip()

    if normal_rules:
        block_width = 0

        for line in cell_block:
            if len(line) > block_width:
                block_width = len(line)

        if start_x[0] == "-":
            start_x = int(start_x[1]) * 2

        if start_y[0] == "-":
            start_y = int(start_y[1]) * 2

        global width, height
        width = int(start_x) + block_width
        height = int(start_y) + len(cell_block)

        if start_x != 0:
            [cell_block.insert(0, '.') for _ in range(start_x + 1)]

        for x in range(len(cell_block.copy())):
            while len(cell_block[x]) <= block_width + start_x:
                cell_block[x] += "."

        for line in cell_block:
            for c in line:
                if c == "*":
                    board.append(1)
                    active_cells.add(cell_block.index(line) * width + line.index(c))
                elif c == ".":
                    board.append(0)

        game(0, load_board=board, rescan=True)


def parse_life_1_06(pattern):
    lines = repr(pattern).split(r'\r\n')

    global width, height
    width = 100
    height = 100

    x_vals = []
    y_vals = []

    for line in lines[1::]:
        if len(line) > 1:
            x_vals.append(int(line.split()[0]))
            y_vals.append(int(line.split()[1]))

    w_padding = (width - len(set(x_vals))) // 2
    h_padding = (height - len(set(y_vals))) // 2

    if min(x_vals) < w_padding:
        diff = abs(min(x_vals)) + w_padding
        for x in range(len(x_vals.copy())):
            x_vals[x] += diff

    if min(y_vals) < h_padding:
        diff = abs(min(y_vals)) + h_padding
        for y in range(len(y_vals.copy())):
            y_vals[y] += diff

    board = new_array()

    for i in range(len(x_vals)):
        board[y_vals[i] * 100 + x_vals[i]] = 1

    game(0, load_board=board, rescan=True)


def parse_plaintext(pattern):
    lines = repr(pattern).split(r'\r\n')
    cell_block = []
    board = []

    max_width = 0

    for line in lines:
        if line[0:1] != "!" and line[0:2] != "'!":
            cell_block.append(line)

            if len(line) > 1:
                max_width = len(line)

    for l in range(len(cell_block.copy())):
        if cell_block[l] == '':
            cell_block[l] = '.' * max_width

    for line in cell_block:
        print(line)
        for c in line:
            if c == "O":
                board.append(1)
            elif c == ".":
                board.append(0)

    global width, height
    width = len(cell_block[0])
    height = len(cell_block)

    for i in range(len(board)):
        x = i % width
        y = floor(i / height)

        print(x, y, board[i])

    game(0, load_board=board, rescan=True)


# def parse_rle(pattern):


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
                if event.key == 306:
                    ctrl_pressed = False
                elif event.key == 27:  # Escape
                    toggle_menu()

                if not textbox_visible:
                    if event.key == 32:  # Space
                        start_generations = True
                    elif event.key == 114:  # R
                        game(steps, load_board=new_array())

        if mouse_down:
            mouse_pos = pygame.mouse.get_pos()
            mouse_rel = pygame.mouse.get_rel()

            if floor(mouse_pos[0] / scale) != floor(old_mouse_pos[0] / scale) or floor(mouse_pos[1] / scale) != floor(old_mouse_pos[1] / scale):
                print(mouse_rel)
                print(sqrt((mouse_rel[0] ** 2) + (mouse_rel[1] ** 2)))
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
