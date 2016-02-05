import sys

import pyglet
import pyglet.gl as gl
from pyglet.window import key

width = 0
height = 0
scale = 0
tolerance = 0.5
dot_counter = 0

game_paused = False
power_up = False
scatter = True

window = pyglet.window.Window(style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
dot_batch = pyglet.graphics.Batch()
stage_batch = pyglet.graphics.Batch()
score_batch = pyglet.graphics.Batch()
life_batch = pyglet.graphics.Batch()
entity_batch = pyglet.graphics.Batch()

fps_display = pyglet.clock.ClockDisplay()

pacman = None
speeds = {}
enemies = {}

active_ghosts = ['red', 'pink']

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
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [3, 3, 3, 3, 3, 3, 0, 1, 3, 3, 3, 0, 0, 0, 3, 0, 0, 0, 0, 3, 3, 3, 1, 0, 3, 3, 3, 3, 3, 3],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
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
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

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
    'pink': (14, 20),
    'cyan': (14, 20),
    'orange': (14, 20)
}

scatter_targets = {
    'red': (29, 40),
    'pink': (0, 40),
    'cyan': (29, -5),
    'orange': (0, -5)
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
        self.speed = 0.08
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
                            self.x -= self.speed * 1.2
                        elif self.d == 'R':
                            self.x += self.speed * 1.2
                        elif self.d == 'U':
                            self.y += self.speed * 1.2
                        elif self.d == 'D':
                            self.y -= self.speed * 1.2

                    else:
                        self.x = x
                        self.y = (board_height + 1 - y)

            if not at_intersection:
                if self.d == 'L':
                    self.vd = 'LR'
                    self.x -= self.speed
                    self.y = round(self.y)

                elif self.d == 'R':
                    self.vd = 'LR'
                    self.x += self.speed
                    self.y = round(self.y)

                elif self.d == 'U':
                    self.vd = 'UD'
                    self.y += self.speed
                    self.x = round(self.x)

                elif self.d == 'D':
                    self.vd = 'UD'
                    self.y -= self.speed
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

                    self.kills += 1
                    self.score += 100 * (2 ** self.kills)
                    draw_score()

        for x, y, big in dots:
            if abs(self.x - x) < 0.3 and abs(self.y - y) < 0.3:
                global dot_counter
                dot_counter += 1

                if dot_counter >= 30 and len(active_ghosts) == 2:
                    active_ghosts.append('cyan')
                elif dot_counter >= 90 and len(active_ghosts) == 3:
                    active_ghosts.append('orange')

                if big:
                    self.score += 50
                    toggle_power_up(None, state=True)
                    pyglet.clock.unschedule(toggle_power_up)
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

        self.color = color
        self.c = ghost_colors[self.color]

        self.r = 14

        self.dead = False

        self.d = 'U'
        self.next_pos = [self.x, self.y]
        self.next_d = None

    def move(self, dt):
        if abs(self.x - round(self.x)) < 0.05 and abs(self.y - round(self.y)) < 0.05:
            self.x, self.y = round(self.x), round(self.y)

            if scatter:
                self.d = get_direction((self.x, self.y), scatter_targets[self.color], self.d)
            else:
                if self.color == 'red':
                    self.d = get_direction((self.x, self.y), (pacman.x, pacman.y), self.d)

                elif self.color == 'pink':
                    if pacman.d == 'U':
                        self.d = get_direction((self.x, self.y), (pacman.x, pacman.y + 4), self.d)
                    elif pacman.d == 'D':
                        self.d = get_direction((self.x, self.y), (pacman.x, pacman.y - 4), self.d)
                    elif pacman.d == 'R':
                        self.d = get_direction((self.x, self.y), (pacman.x + 4, pacman.y), self.d)
                    elif pacman.d == 'L':
                        self.d = get_direction((self.x, self.y), (pacman.x - 4, pacman.y), self.d)
                    else:
                        self.d = get_direction((self.x, self.y), (pacman.x, pacman.y), self.d)

                elif self.color == 'cyan':
                    self.d = get_direction((self.x, self.y), (pacman.x + (pacman.x - enemies['pink'].x), pacman.y + (pacman.y - enemies['pink'].y)), self.d)

                elif self.color == 'orange':
                    if distance((self.x, self.y), (pacman.x, pacman.y)) > 8:
                        self.d = get_direction((self.x, self.y), (pacman.x, pacman.y), self.d)
                    else:
                        self.d = get_direction((self.x, self.y), (2, 4), self.d)

                if (self.x, self.y) == spawn_positions[self.color]:
                    self.d = 'U'

        self.x, self.y = [x + y for x, y in zip([self.x, self.y], speeds[self.d])]

    def draw(self):
        draw_circle(self.x, self.y, self.r, self.c, entity_batch)


def set_speeds(speed):
    global speeds
    speeds = {
        'U': [0, speed],
        'D': [0, -speed],
        'L': [-speed, 0],
        'R': [speed, 0],
        None: [0, 0]
    }


def toggle_power_up(dt, state=False):
    global power_up
    power_up = state

    if power_up:
        set_speeds(0.05)

        for enemy in enemies:
            if enemies[enemy].c != (1.0, 1.0, 1.0):
                enemies[enemy].c = (0.0, 0.0, 1.0)

    else:
        set_speeds(0.075)

        for enemy in enemies:
            enemies[enemy].c = ghost_colors[enemies[enemy].color]
            enemies[enemy].r = 14
            enemies[enemy].dead = False


def toggle_mode(dt):
    global scatter

    if scatter:
        scatter = False
        pyglet.clock.schedule_once(toggle_mode, 7)
    else:
        scatter = True
        pyglet.clock.schedule_once(toggle_mode, 20)


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


def distance(a, b):
    return (abs(a[0] - b[0]) + abs(a[1] - b[1])) ** 0.5


def get_direction(pos, goal, direction):
    neighbors = []
    pos, goal = (round(pos[0]), round(board_height + 1 - pos[1])), (round(goal[0]), round(board_height + 1 - goal[1]))

    for y in range(-1, 2):
        for x in range(-1, 2):
            if abs(x) != abs(y) and 0 <= pos[0] + x < board_width and 0 <= pos[1] + y < board_height and board[pos[1] + y][pos[0] + x] > 0:
                next_dir = direction

                if x == 1:
                    if direction == 'L':
                        continue
                    next_dir = 'R'

                elif x == -1:
                    if direction == 'R':
                        continue
                    next_dir = 'L'

                elif y == 1:
                    if direction == 'U':
                        continue
                    next_dir = 'D'

                elif y == -1:
                    if direction == 'D':
                        continue
                    next_dir = 'U'

                neighbors.append((next_dir, distance((pos[0] + x, pos[1] + y), goal)))

    smallest_dist = min(neighbors, key=lambda l: l[1])
    matches = []
    directions = []

    for neighbor in neighbors:
        if neighbor[1] == smallest_dist[1]:
            matches.append(neighbor)
            directions.append(neighbor[0])

    if len(matches) > 1:
        if 'U' in directions:
            return 'U'
        if 'L' in directions:
            return 'L'
        if 'D' in directions:
            return 'D'
        if 'R' in directions:
            return 'R'
    else:
        return smallest_dist[0]


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
    for enemy in enemies:
        enemies[enemy].x, enemies[enemy].y = spawn_positions[enemy]
        enemies[enemy].d = 'U'

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

    for enemy in active_ghosts:
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

    fps_display.draw()

    entity_batch = pyglet.graphics.Batch()


def start():
    gl.glClearColor(0.0, 0.0, 0.0, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    global width, height, scale, pacman
    pacman = Pacman()
    scale = 20

    w = board_width * scale
    h = board_height * scale + 100

    window.set_size(w, h)
    x, y = window.get_location()
    window.set_location(x, y - 150)

    width = w // scale
    height = h // scale

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
    set_speeds(0.075)

    pyglet.clock.schedule_once(toggle_mode, 7)
    pyglet.clock.schedule_interval(game_loop, 1 / 60)

    pyglet.app.run()

start()
