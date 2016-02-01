import sys
from random import choice

import pyglet
import pyglet.gl as gl
from pyglet.window import key

width = 0
height = 0
scale = 0
tolerance = 0.5

game_paused = False
power_up = False

window = pyglet.window.Window(style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
dot_batch = pyglet.graphics.Batch()
stage_batch = pyglet.graphics.Batch()
score_batch = pyglet.graphics.Batch()
life_batch = pyglet.graphics.Batch()
entity_batch = pyglet.graphics.Batch()

pacman = None
enemies = {}

nodes = None
dots = set()
walls = set()
intersections = {(15, 10, 'LR')}

board = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 2, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 3, 0, 0, 3, 3, 0, 0, 3, 3, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 3, 0, 3, 3, 3, 3, 0, 3, 3, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 0, 3, 3, 3, 3, 0, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 3, 0, 3, 3, 3, 3, 0, 3, 3, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 2, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 2, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

board_height = len(board)
board_width = len(board[0])

wall_vertices = {
    'left': [(9, 0, 2, 20)],
    'right': [(9, 0, 2, 20)],
    'top': [(0, 9, 20, 2)],
    'bottom': [(0, 9, 20, 2)],

    'topleft': [(9, 0, 2, 6), (9, 6, 2, 1), (10, 7, 2, 1), (11, 8, 2, 1), (12, 9, 2, 1), (13, 10, 2, 1), (14, 9, 6, 2)],
    'topright': [(9, 0, 2, 6), (9, 6, 2, 1), (8, 7, 2, 1), (7, 8, 2, 1), (6, 9, 2, 1), (5, 10, 2, 1), (0, 9, 6, 2)],
    'bottomleft': [(9, 20, 2, -6), (9, 14, 2, -1), (10, 13, 2, -1), (11, 12, 2, -1), (12, 11, 2, -1), (13, 10, 2, -1), (14, 11, 6, -2)],
    'bottomright': [(9, 20, 2, -6), (5, 10, 2, -1), (6, 11, 2, -1), (7, 12, 2, -1), (8, 13, 2, -1), (9, 14, 2, -1), (0, 11, 6, -2)]
}
text_vertices = {
    '0': [(6, 0, 9, 3), (3, 3, 6, 3), (0, 6, 6, 8), (3, 14, 3, 3), (6, 17, 9, 3), (12, 14, 6, 3), (15, 6, 6, 8), (15, 3, 3, 3)],
    '1': [(0, 0, 18, 3), (6, 3, 6, 17), (3, 14, 3, 3)],
    '2': [(0, 0, 21, 3), (0, 3, 9, 3), (3, 6, 12, 2), (6, 8, 9, 3), (12, 11, 9, 3), (15, 14, 6, 3), (3, 17, 15, 3), (0, 14, 6, 3)],
    '3': [(0, 3, 6, 3), (3, 0, 15, 3), (15, 3, 6, 6), (6, 9, 12, 3), (9, 12, 6, 3), (12, 15, 6, 2), (0, 17, 21, 3)],
    '4': [(12, 0, 6, 20), (0, 6, 21, 3), (0, 9, 6, 3), (3, 12, 6, 3), (6, 15, 6, 2), (9, 17, 3, 3)],
    '5': [(0, 3, 6, 3), (3, 0, 15, 3), (15, 3, 6, 8), (0, 11, 18, 3), (0, 14, 6, 6), (6, 17, 12, 3)],
    '6': [(3, 0, 15, 3), (15, 3, 6, 5), (0, 3, 6, 5), (0, 8, 18, 3), (0, 11, 6, 3), (3, 14, 6, 3), (6, 17, 12, 3)],
    '7': [(6, 0, 6, 8), (9, 8, 6, 3), (12, 11, 6, 3), (15, 14, 6, 6), (0, 14, 6, 6), (6, 17, 9, 3)],
    '8': [(3, 0, 15, 3), (0, 3, 3, 5), (15, 3, 6, 5), (9, 5, 6, 3), (3, 8, 12, 3), (0, 11, 9, 3), (0, 14, 6, 3), (3, 17, 12, 3), (15, 11, 3, 6)],
    '9': [(3, 0, 12, 3), (12, 3, 6, 3), (15, 6, 6, 11), (3, 9, 12, 3), (0, 12, 6, 5), (3, 17, 15, 3)],

    'C': [(15, 3, 6, 3), (6, 0, 12, 3), (3, 3, 6, 3), (0, 6, 6, 9), (3, 14, 6, 3), (6, 17, 12, 3), (15, 14, 6, 3)],
    'E': [(0, 0, 6, 20), (6, 0, 15, 3), (6, 9, 15, 3), (6, 17, 15, 3)],
    'G': [(6, 17, 14, 3), (3, 14, 6, 3), (0, 6, 6, 9), (3, 3, 6, 3), (6, 0, 14, 3), (14, 3, 6, 9), (11, 9, 3, 3)],
    'H': [(0, 0, 6, 20), (3, 9, 9, 3), (12, 0, 6, 20)],
    'I': [(0, 0, 18, 3), (6, 3, 6, 14), (0, 17, 18, 3)],
    'O': [(3, 0, 14, 3), (0, 3, 6, 14), (3, 17, 15, 3), (15, 3, 6, 14)],
    'P': [(0, 0, 6, 20), (6, 17, 12, 3), (15, 8, 5, 9), (6, 6, 12, 3)],
    'R': [(0, 0, 6, 20), (6, 17, 12, 3), (15, 11, 6, 9), (12, 9, 9, 3), (6, 6, 9, 3), (9, 3, 9, 3), (12, 0, 9, 3)],
    'S': [(0, 3, 6, 3), (3, 0, 15, 3), (15, 3, 5, 6), (3, 9, 15, 3), (0, 12, 6, 5), (3, 17, 12, 3), (12, 14, 6, 3)],
    'U': [(0, 3, 6, 17), (3, 0, 12, 3), (12, 3, 6, 17)],
}

text_positions = [
    (3, -2.8, '1'), (4, -2.8, 'U'), (5.1, -2.8, 'P'),
    (10, -2.8, 'H'), (11.05, -2.8, 'I'), (12, -2.8, 'G'), (13.3, -2.8, 'H'),
    (15, -2.8, 'S'), (16.2, -2.8, 'C'), (17.4, -2.8, 'O'), (18.6, -2.8, 'R'), (19.8, -2.8, 'E'),
]

spawn_positions = {
    'red': (14, 20),
    'pink': (15, 20),
    'cyan': (14, 19),
    'orange': (15, 19)
}

ghost_colors = {
    'red': (1.0, 0.0, 0.0),
    'pink': (1.0, 0.75294, 0.79607),
    'cyan': (0.0, 1.0, 1.0),
    'orange': (1.0, 0.54901, 0.0)
}

circle_vertices = {}
dot_vertex_lists = {}


class Pacman:
    def __init__(self):
        self.x = 14.5
        self.y = 10
        self.r = 14
        self.d = None
        self.vd = 'LR'
        self.speed = 3
        self.score = 0
        self.lives = 3
        self.kills = 0

    def move(self, dt):
        if self.d is not None and self.d in self.vd:
            at_intersection = False

            for x, y, d in intersections:
                if abs(self.x - x) < 0.3 and abs(((board_height + 1) - self.y) - y) < 0.3:
                    at_intersection = True
                    self.vd = d

                    if self.d in d:
                        if self.d == 'L':
                            self.x -= self.speed * dt
                        elif self.d == 'R':
                            self.x += self.speed * dt
                        elif self.d == 'U':
                            self.y += self.speed * dt
                        elif self.d == 'D':
                            self.y -= self.speed * dt

                    else:
                        self.x = x
                        self.y = (board_height + 1 - y)

            if not at_intersection:
                if self.d == 'L':
                    self.vd = 'LR'
                    self.x -= self.speed * dt
                    self.y = round(self.y)

                elif self.d == 'R':
                    self.vd = 'LR'
                    self.x += self.speed * dt
                    self.y = round(self.y)

                elif self.d == 'U':
                    self.vd = 'UD'
                    self.y += self.speed * dt
                    self.x = round(self.x)

                elif self.d == 'D':
                    self.vd = 'UD'
                    self.y -= self.speed * dt
                    self.x = round(self.x)

    def col_detect(self):
        global dot_batch

        for color in enemies:
            enemy = enemies[color]

            if enemy.dead:
                continue

            if (abs((self.x + self.r) - (enemy.x + self.r)) ** 2 + abs((self.y + self.r) - (enemy.y + self.r))) ** 0.5 <= ((self.r + enemy.r) / scale):
                if not power_up:
                    if self.lives == 0:
                        return game_over()
                    else:
                        self.lives -= 1
                        draw_lives()

                        return reset()
                else:
                    enemy.dead = True
                    enemy.c = (1.0, 1.0, 1.0)
                    enemy.r = 5
                    enemy.goal = Node(spawn_positions[enemy.color][0], (board_height + 1) - spawn_positions[enemy.color][1])

                    self.kills += 1
                    self.score += 100 * (2 ** self.kills)
                    draw_score()

        for x, y, big in dots:
            if abs(self.x - x) < 0.3 and abs(self.y - y) < 0.3:
                if big:
                    self.score += 50
                    toggle_power_up(None)
                    pyglet.clock.schedule_once(toggle_power_up, 20)
                else:
                    self.score += 10

                dots.discard((x, y, big))
                dot_vertex_lists[(x, y)].delete()
                draw_score()

                return

    def draw(self):
        draw_circle(self.x, self.y, self.r, (1.0, 1.0, 0.0), entity_batch)


class Enemy:
    def __init__(self, color):
        self.x, self.y = spawn_positions[color]
        self.r = 14
        self.d = None
        self.speed = 2
        self.color = color
        self.c = ghost_colors[self.color]
        self.goal = None
        self.dead = False

    def move(self, dt):
        goal = None

        if not self.dead:
            if power_up and self.goal is not None:
                if abs(self.x - self.goal.x) <= 0.3 and abs(board_height + 1 - self.y - self.goal.y) <= 0.3:
                    self.goal = get_random_node()

            elif self.goal is not None:
                if abs(self.x - self.goal.x) <= 0.3 and abs(board_height + 1 - self.y - self.goal.y) <= 0.3:
                    self.goal = None

        if self.goal is None:
            if self.color == 'red':
                goal = Node(pacman.x, board_height + 1 - pacman.y)
            elif self.color == 'pink' or self.color == 'cyan':
                if pacman.d is not None:
                    goal_found = False
                    neighbors = get_neighbors(Node(round(pacman.x), round(board_height + 1 - pacman.y)))

                    if pacman.d == 'U':
                        goal = (round(pacman.x), round(board_height - pacman.y))
                    elif pacman.d == 'D':
                        goal = (round(pacman.x), round(board_height + 2 - pacman.y))
                    elif pacman.d == 'L':
                        goal = (round(pacman.x - 1), round(board_height + 1 - pacman.y))
                    elif pacman.d == 'R':
                        goal = (round(pacman.x + 1), round(board_height + 1 - pacman.y))

                    for node in neighbors:
                        if goal[0] == node.x and goal[1] == node.y:
                            goal_found = True
                            goal = Node(node.x, node.y)
                            break

                    if not goal_found:
                        goal = Node(pacman.x, board_height + 1 - pacman.y)
                else:
                    goal = Node(pacman.x, board_height + 1 - pacman.y)
            elif self.color == 'orange':
                if (abs(self.x - pacman.x) ** 2 + abs(self.y - pacman.y) ** 2) ** 0.5 <= 8:
                    goal = Node(2, 30)
                else:
                    goal = Node(pacman.x, board_height + 1 - pacman.y)

        if self.goal is not None:
            goal = self.goal

        for node, d in a_star(Node(self.x, board_height + 1 - self.y), goal):
            if abs(self.x - node.x) < 0.3 and abs((board_height + 1 - self.y) - node.y) < 0.3:
                self.d = d
                break

        if self.d == 'L':
            self.y = round(self.y)
            self.x -= self.speed * dt
        elif self.d == 'R':
            self.y = round(self.y)
            self.x += self.speed * dt
        elif self.d == 'U':
            self.x = round(self.x)
            self.y += self.speed * dt
        elif self.d == 'D':
            self.x = round(self.x)
            self.y -= self.speed * dt

    def draw(self):
        draw_circle(self.x, self.y, self.r, self.c, entity_batch)


class Node:
    def __init__(self, x, y):
        self.x = round(x)
        self.y = round(y)
        self.parent = None
        self.H = 0
        self.G = 0


def get_random_node():
    node = choice(choice(nodes))

    if board[node.y][node.x] != 0:
        if (abs(node.x - pacman.x) ** 2 + abs(board_height + 1 - node.y - pacman.y) ** 2) ** 0.5 >= 20:
            return Node(node.x, node.y)
        else:
            return get_random_node()
    else:
        return get_random_node()


def toggle_power_up(dt):
    global power_up
    power_up = not power_up

    if power_up:
        for enemy in enemies:
            enemies[enemy].c = (0.0, 0.0, 1.0)
            enemies[enemy].goal = get_random_node()

    else:
        for enemy in enemies:
            enemies[enemy].c = ghost_colors[enemies[enemy].color]
            enemies[enemy].r = 14
            enemies[enemy].goal = None
            enemies[enemy].dead = False


def draw_rect(x, y, c, batch):
    r, g, b = c
    padding_lt = 1
    padding_rb = 1

    batch.add(4, gl.GL_QUADS, None,
              ('v2f', (x * scale + padding_lt, y * scale + padding_lt,
                       x * scale + scale - padding_rb, y * scale + padding_lt,
                       x * scale + scale - padding_rb, y * scale + scale - padding_rb,
                       x * scale + padding_lt, y * scale + scale - padding_rb)),
              ('c3f', (r, g, b, r, g, b, r, g, b, r, g, b)))


def draw_sub_rect(x, y, sx, sy, sw, sh, c, batch):
    r, g, b = c

    batch.add(4, gl.GL_QUADS, None, (
        'v2f', (
            (x * scale) + sx, (y * scale) + sy,
            (x * scale) + sx + sw, (y * scale) + sy,
            (x * scale) + sx + sw, (y * scale) + sy + sh,
            (x * scale) + sx, (y * scale) + sy + sh)
    ), (
        'c3f', (r, g, b, r, g, b, r, g, b, r, g, b)))


def generate_circle(radius):
    verts = set()
    added_verts = set()

    if radius not in circle_vertices:
        circle_vertices[radius] = []

    for sy in range(-radius, radius + 1):
        for sx in range(-radius, radius + 1):
            if (sx ** 2 + sy ** 2) ** 0.5 - radius <= tolerance:
                verts.add((round((sx + radius + (scale / 2 - radius))), round(sy + radius + (scale / 2 - radius))))

    for x, y in verts:
        if (x, y) not in added_verts:
            cell_width = radius * 2
            cell_height = radius * 2

            while cell_width > 0 and cell_height > 0:
                fits = True

                if (x + cell_width, y) not in verts:
                    fits = False
                    cell_width -= 1

                if (x, y + cell_height) not in verts:
                    fits = False
                    cell_height -= 1

                if (x + cell_width, y + cell_height) not in verts:
                    fits = False
                    if (x + cell_width, y + cell_height - 1) in verts:
                        cell_height -= 1
                    elif (x + cell_width - 1, y + cell_height) in verts:
                        cell_width -= 1
                    else:
                        cell_height -= 1
                        cell_width -= 1

                if fits:
                    break

            circle_vertices[radius].append((x, y, cell_width, cell_height))

            for vx in range(x, x + cell_width):
                for vy in range(y, y + cell_height):
                    added_verts.add((vx, vy))


def draw_circle(x, y, radius, c, batch, dot=False):
    if radius not in circle_vertices:
        generate_circle(radius)

    if dot:
        r, g, b = c

        vertices = []
        colors = []

        for sx, sy, sw, sh in circle_vertices[radius]:
            vertices.extend([(x * scale) + sx, (y * scale) + sy, (x * scale) + sx + sw, (y * scale) + sy, (x * scale) + sx + sw, (y * scale) + sy + sh, (x * scale) + sx, (y * scale) + sy + sh])
            colors.extend([r, g, b, r, g, b, r, g, b, r, g, b])

        dot_vertex_lists[(x, y)] = batch.add(len(circle_vertices[radius]) * 4, gl.GL_QUADS, None, ('v2f', vertices), ('c3f', colors))
    else:
        for sx, sy, sw, sh in circle_vertices[radius]:
            draw_sub_rect(x, y, sx, sy, sw, sh, c, batch)


def distance(node1, node2):
    return abs(node1.x - node2.x) + abs(node1.y - node2.y)


def get_neighbors(node):
    neighbors = []

    for sy in range(-1, 2):
        for sx in range(-1, 2):
            if not abs(sx) == abs(sy) and 0 <= node.x + sx < board_width and 0 <= node.y + sy < board_height and board[node.y + sy][node.x + sx] > 0:
                neighbors.append(nodes[node.y + sy][node.x + sx])

    return neighbors


def get_path(path):
    index = 0

    for node in path.copy():
        if index < len(path) - 1:
            next_node = path[index + 1]

            if node.x == next_node.x:
                if node.y > next_node.y:
                    path[index] = (node, 'U')
                else:
                    path[index] = (node, 'D')
            else:
                if node.x > next_node.x:
                    path[index] = (node, 'L')
                else:
                    path[index] = (node, 'R')

            index += 1

    return path[:-1:]


def a_star(initial, goal):
    open_set = set()
    closed_set = set()

    current = initial
    open_set.add(current)

    while open_set:
        current = min(open_set, key=lambda o: o.G + o.H)

        if current.x == goal.x and current.y == goal.y:
            path = []

            while current.parent:
                path.append(current)
                current = current.parent

            path.append(current)
            return get_path(path[::-1])

        open_set.remove(current)
        closed_set.add(current)

        for node in get_neighbors(current):
            if node in closed_set:
                continue

            if node in open_set:
                new_g = current.G + 1

                if node.G > new_g:
                    node.G = new_g
                    node.parent = current
            else:
                node.G = current.G + 1
                node.H = distance(node, goal)
                node.parent = current
                open_set.add(node)

    raise ValueError('No Path Found')


def parse_board():
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] > 0 and 0 < x < board_width - 1 and 0 < y < board_height - 1:
                directions = ""

                for sy in range(-1, 2):
                    for sx in range(-1, 2):
                        if not abs(sx) == abs(sy) and board[y + sy][x + sx] > 0:
                            if sx == -1:
                                directions += "L"
                            if sx == 1:
                                directions += "R"
                            if sy == -1:
                                directions += "U"
                            if sy == 1:
                                directions += "D"

                if directions != "DU" and directions != "LR":
                    intersections.add((x, y, directions))

            if board[y][x] == 1 or board[y][x] == 2:
                dots.add((x, board_height + 1 - y, board[y][x] == 2))

            elif board[y][x] == 0:
                if y > 0 and board[y - 1][x] == 0:                              # Bottom
                    if y < board_height - 1 and board[y + 1][x] == 0:           # Bottom and Top
                        if x == 0 or board[y][x - 1] != 0:
                            walls.add((x, y, 'left'))

                        elif x == board_width - 1 or board[y][x + 1] != 0:
                            walls.add((x, y, 'right'))

                        if x > 0 and board[y][x - 1] == 0:                      # Bottom and Top and Left
                            if x < board_width - 1 and board[y][x + 1] == 0:    # Bottom and Top and Left and Right
                                diagonals = [1 if board[y + a][x + b] > 0 else 0 for a in [-1, 1] for b in [-1, 1]]

                                if sum(diagonals) == 1:
                                    if diagonals[0] == 1:
                                        walls.add((x, y, 'bottomright'))
                                    elif diagonals[1] == 1:
                                        walls.add((x, y, 'bottomleft'))
                                    elif diagonals[2] == 1:
                                        walls.add((x, y, 'topright'))
                                    elif diagonals[3] == 1:
                                        walls.add((x, y, 'topleft'))

                    elif x > 0 and board[y][x - 1] == 0:                        # Bottom and Left and Not Top
                        if x < board_width - 1 and board[y][x + 1] == 0:        # Bottom and Left and Right and Not Top
                            walls.add((x, y, 'top'))
                        else:                                                   # Bottom and Left and Not Top and Not Right
                            walls.add((x, y, 'bottomright'))

                    elif x < board_width - 1 and board[y][x + 1] == 0:          # Bottom and Right and Not Top
                        if x == 0 or board[y][x - 1] != 0:                      # Bottom and Right and Not Top and Not Left
                            walls.add((x, y, 'bottomleft'))

                elif y < board_height - 1 and board[y + 1][x] == 0:             # Top and Not Bottom
                    if x > 0 and board[y][x - 1] == 0:                          # Top and Left and Not Bottom
                        if x < board_width - 1 and board[y][x + 1] == 0:        # Top and Left and Right and Not Bottom
                            walls.add((x, y, 'bottom'))
                        else:                                                   # Top and Left and Not Bottom and Not Right
                            walls.add((x, y, 'topright'))

                    elif x < board_width - 1 and board[y][x + 1] == 0:          # Top and Right and Not Bottom and Not Left
                        walls.add((x, y, 'topleft'))

                elif x > 0 and board[y][x - 1] == 0:                            # Left
                    if x < board_width - 1 and board[y][x + 1] == 0:            # Left and Right
                        if y == 0 or board[y - 1][x] != 0:                      # Left and Right and Not Top
                            walls.add((x, y, 'top'))
                        elif y == board_height - 1 or board[y + 1][x] != 0:     # Left and Right and Not Bottom
                            walls.add((x, y, 'bottom'))


def draw_board():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    for x, y, direction in walls:
        [draw_sub_rect(x, height - y - 4, sx, sy, sw, sh, (0.0, 0.0, 1.0), stage_batch) for sx, sy, sw, sh in wall_vertices[direction]]


def draw_dots():
    for x, y, big in dots:
        if big:
            draw_circle(x, y, 8, (1.0, 1.0, 0.0), dot_batch, dot=True)
        else:
            draw_circle(x, y, 2, (1.0, 1.0, 0.0), dot_batch, dot=True)


def draw_lives():
    global life_batch
    life_batch = pyglet.graphics.Batch()
    x_pos = 5

    for l in str(pacman.lives):
        [draw_sub_rect(x_pos, height - 2.5, sx, sy, sw, sh, (1.0, 1.0, 1.0), life_batch) for sx, sy, sw, sh in text_vertices[l]]
        x_pos += 1.2


def draw_score():
    global score_batch
    score_batch = pyglet.graphics.Batch()
    x_pos = 16

    for d in str(pacman.score):
        [draw_sub_rect(x_pos, height - 2.5, sx, sy, sw, sh, (1.0, 1.0, 1.0), score_batch) for sx, sy, sw, sh in text_vertices[d]]
        x_pos += 1.2


def draw_ui():
    for x, y, c in text_positions:
        [draw_sub_rect(x, height - y - 4, sx, sy, sw, sh, (1.0, 1.0, 1.0), stage_batch) for sx, sy, sw, sh in text_vertices[c]]


def reset():
    enemies['red'].x, enemies['red'].y = 14, 20
    enemies['pink'].x, enemies['pink'].y = 15, 20
    enemies['cyan'].x, enemies['cyan'].y = 14, 19
    enemies['orange'].x, enemies['orange'].y = 15, 19

    pacman.x, pacman.y = 14.5, 10
    pacman.vd = 'LR'
    pacman.d = None


def game_over():
    pyglet.clock.unschedule(game_loop)
    print("Game Over!")
    sys.exit()


def game_loop(dt):
    pacman.move(dt)
    pacman.col_detect()

    for enemy in enemies:
        enemies[enemy].move(dt)


@window.event
def on_key_press(symbol, modifers):
    if symbol == key.LEFT:
        if 'L' in pacman.vd:
            pacman.d = 'L'
    elif symbol == key.RIGHT:
        if 'R' in pacman.vd:
            pacman.d = 'R'
    elif symbol == key.UP:
        if 'U' in pacman.vd:
            pacman.d = 'U'
    elif symbol == key.DOWN:
        if 'D' in pacman.vd:
            pacman.d = 'D'
    elif symbol == key.P:
        global game_paused
        game_paused = not game_paused
        if game_paused:
            pyglet.clock.unschedule(game_loop)
        else:
            pyglet.clock.schedule_interval(game_loop, 1 / 60)


@window.event
def on_draw():
    global entity_batch

    window.clear()

    stage_batch.draw()

    score_batch.draw()
    life_batch.draw()

    dot_batch.draw()

    pacman.draw()

    for enemy in enemies:
        enemies[enemy].draw()

    entity_batch.draw()

    entity_batch = pyglet.graphics.Batch()


def start():
    gl.glClearColor(0.0, 0.0, 0.0, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    global width, height, scale, pacman, nodes
    pacman = Pacman()
    scale = 20

    w = board_width * scale
    h = board_height * scale + 100

    window.set_size(w, h)
    x, y = window.get_location()
    window.set_location(x, y - 150)

    width = w // scale
    height = h // scale

    nodes = [[Node(x, y) for x in range(board_width)] for y in range(board_height)]

    enemies['red'] = Enemy('red')
    enemies['pink'] = Enemy('pink')
    enemies['cyan'] = Enemy('cyan')
    enemies['orange'] = Enemy('orange')

    parse_board()
    draw_board()
    draw_dots()
    draw_ui()
    draw_score()
    draw_lives()

    pyglet.clock.schedule_interval(game_loop, 1 / 60)

    pyglet.app.run()

start()
