import sys
from time import clock

import pygame

from math import floor

screen = None

active_cells = set()


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


def cell_check(board, width, height, infinite):
    new_board = new_array(height, width)

    if infinite:
        x_range = range(width)
        y_range = range(height)
    else:
        x_range = range(1, width - 1)
        y_range = range(1, height - 1)

    if not active_cells:
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

                field_sum = sum([board[a][b] for a in y_vals for b in x_vals])
                old_value = board[y][x]

                if field_sum == 3:
                    new_board[y][x] = 1
                    active_cells.add((x, y))
                elif field_sum != 4:
                    new_board[y][x] = 0
                else:
                    new_board[y][x] = old_value
    else:
        for x, y in active_cells.copy():
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

                    field_sum = sum([board[a][b] for a in y_vals for b in x_vals])
                    old_value = board[cy][cx]

                    if field_sum == 3:
                        new_board[cy][cx] = 1

                        if (cx, cy) not in active_cells:
                            active_cells.add((cx, cy))

                    elif field_sum != 4:
                        active_cells.discard((cx, cy))
                    else:
                        new_board[cy][cx] = old_value

    return new_board


def draw_image(scale):
    screen.fill((255, 255, 255))

    for x, y in active_cells:
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
    draw_image(scale)

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

                    t1 = clock()
                    board = cell_check(board, x, y, infinite)
                    draw_image(scale)
                    t2 = clock()

                    print("Loop time: " + str((t2 - t1) * 1000) + " ms")
                    print("Active cells: " + str(len(active_cells)))


def start(x, y, steps, delay, scale, infinite=True):
    pygame.init()

    global screen
    screen = pygame.display.set_mode((x * scale, y * scale))
    screen.fill((255, 255, 255))

    game(x, y, steps, delay, scale, infinite)

start(1000, 1000, 0, 0, 1)
