import pickle
import sys

import pygame

from math import floor

screen = None
menu_visible = False

width = 0
height = 0
scale = 0
delay = 0

buttons = {}
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


def new_array():
    return [0] * (height * width)


def toggle_cell(x, y, state):
    rect = (x * scale, y * scale, scale, scale)

    if state == 1:
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

            if field_sum == 3:
                new_board[i] = 1
                active_cells.add(i)
            elif field_sum != 4:
                new_board[i] = 0
            else:
                new_board[i] = board[i]
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

    game(0, load_board=pickle.load(open('save_file.txt', 'rb')))


def game(steps, load_board=None):
    if load_board is not None:
        board = cell_check(load_board, rescan=True)
    else:
        board = cell_check(new_array())

    current_step = 0
    start_generations = False
    mouse_down = False
    mouse_button_down = 0
    old_mouse_pos = (-1, -1)

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

                            elif button.name.lower() == "quit":
                                pygame.quit()
                                sys.exit()

            elif event.type == pygame.MOUSEBUTTONUP:
                if not menu_visible:
                    mouse_down = False
                    old_mouse_pos = (-1, -1)

            elif event.type == pygame.KEYUP:
                if event.key == 27:  # Escape
                    toggle_menu()
                elif event.key == 32:  # Space
                    start_generations = True
                elif event.key == 114:  # R
                    game(steps, load_board=new_array())

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
    buttons['quit'] = Button("Quit")

    global screen
    screen = pygame.display.set_mode((width * scale, height * scale))
    screen.fill((255, 255, 255))

    game(steps)

start(250, 250, 0, 0, 4)
