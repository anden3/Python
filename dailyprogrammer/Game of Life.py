import sys

import pygame

from math import floor

screen = None


def new_array(height, width):
    return [[0 for _ in range(width)] for _ in range(height)]


def toggle_cell(x, y, scale, state):
    rect = (x * scale, y * scale, scale, scale)

    if state == 1:
        screen.fill((0, 0, 0), rect=rect)
    else:
        screen.fill((255, 255, 255), rect=rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    pygame.display.update(rect)


def click_handler(pos, board, scale, button):
    cell_x = floor(pos[0] / scale)
    cell_y = floor(pos[1] / scale)

    if board[cell_y][cell_x] == 1 and button == 3:
        board[cell_y][cell_x] = 0
        toggle_cell(cell_x, cell_y, scale, 0)
    elif board[cell_y][cell_x] == 0 and button == 1:
        board[cell_y][cell_x] = 1
        toggle_cell(cell_x, cell_y, scale, 1)


def draw_grid(width, height, scale):
    screen.fill((255, 255, 255))

    for y in range(height):
        for x in range(width):
            pygame.draw.rect(screen, (0, 0, 0), (x * scale, y * scale, scale, scale), 1)


def cell_check(board, width, height, infinite):
    new_board = new_array(height, width)

    if infinite:
        x_range = range(width)
        y_range = range(height)
    else:
        x_range = range(1, width - 1)
        y_range = range(1, height - 1)

    for y in y_range:
        for x in x_range:
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

            neighbor_sum = sum([board[a][b] for a in y_vals for b in x_vals]) - board[y][x]

            if board[y][x] == 1 and 3 < neighbor_sum < 2:
                new_board[y][x] = 0
            elif board[y][x] == 1 and (neighbor_sum == 2 or neighbor_sum == 3):
                new_board[y][x] = 1
            elif board[y][x] == 0 and neighbor_sum == 3:
                new_board[y][x] = 1

    return new_board


def draw_image(board, scale):
    draw_grid(len(board[0]), len(board), scale)

    for y in range(len(board)):
        for x in range(len(board[y])):
            if board[y][x] == 1:
                rect = (x * scale, y * scale, scale, scale)
                screen.fill((0, 0, 0), rect=rect)

    pygame.display.flip()


def game(x, y, steps, delay, scale, infinite):
    board = new_array(y, x)

    current_step = 0
    start_generations = False
    mouse_down = False
    mouse_button_down = 0

    last = pygame.time.get_ticks()
    old_mouse_pos = (-1, -1)

    board = cell_check(board, x, y, infinite)
    draw_image(board, scale)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
                mouse_button_down = event.button
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False
                old_mouse_pos = (-1, -1)
            elif event.type == pygame.KEYUP:
                if event.key == 27:  # Escape
                    sys.exit()
                elif event.key == 32:  # Space
                    start_generations = True
                elif event.key == 114:  # R
                    game(x, y, steps, delay, scale, infinite)

        if mouse_down:
            mouse_pos = pygame.mouse.get_pos()

            if floor(mouse_pos[0] / scale) != floor(old_mouse_pos[0] / scale) or floor(mouse_pos[1] / scale) != floor(old_mouse_pos[1] / scale):
                old_mouse_pos = mouse_pos
                click_handler(mouse_pos, board, scale, mouse_button_down)

        now = pygame.time.get_ticks()

        if start_generations:
            if now - last >= delay:
                if steps == 0 or current_step < steps:
                    current_step += 1
                    last = now

                    board = cell_check(board, x, y, infinite)
                    draw_image(board, scale)


def start(x, y, steps, delay, scale, infinite=True):
    pygame.init()

    global screen
    screen = pygame.display.set_mode((x * scale, y * scale))

    game(x, y, steps, delay, scale, infinite)

start(50, 50, 0, 100, 20)
