import random
from time import perf_counter

import pyglet
import pyglet.gl as gl

width = 0
height = 0

mouse_pos = (50, 50)

enemies = {}

batch = pyglet.graphics.Batch()
window = pyglet.window.Window()

now = perf_counter()
last = perf_counter()
delta_time = 0


class Enemy:
    def __init__(self):
        self.x, self.y = spawn_random()
        self.width = random.randint(1, 9)
        self.color = (random.random(), random.random(), random.random())
        self.speed = 0.1
        self.dx = 0
        self.dy = 0

        self.player_dist()

    def draw(self):
        r, g, b = self.color

        batch.add(4, gl.GL_QUADS, None,
              ('v2f', (self.x, self.y,
                       self.x + self.width, self.y,
                       self.x + self.width, self.y + self.width,
                       self.x, self.y + self.width)),
              ('c3f', (r, g, b, r, g, b, r, g, b, r, g, b)))

    def player_dist(self):
        self.dx = mouse_pos[0] - (self.x + (self.width / 2))
        self.dy = mouse_pos[1] - (self.y + (self.width / 2))

    def move_to_player(self):
        self.x += self.dx * delta_time * self.speed
        self.y += self.dy * delta_time * self.speed


def update_delta():
    global now, last, delta_time
    now = perf_counter()
    delta_time = (now - last)
    last = now


def draw_enemies():
    global batch
    batch = pyglet.graphics.Batch()

    for enemy in enemies:
        enemies[enemy].draw()

    batch.draw()


def move_enemies():
    update_delta()

    for enemy in enemies:
        enemies[enemy].player_dist()
        enemies[enemy].move_to_player()


def spawn_random():
    axis = ('x' if random.random() > 0.5 else 'y')
    position = random.randint(0, (width if axis == 'x' else height))

    if axis == 'x':
        other_pos = (0 if random.random() > 0.5 else height)
        return position, other_pos
    else:
        other_pos = (0 if random.random() > 0.5 else width)
        return other_pos, position


def update(dt):
    move_enemies()


def spawn_enemy(dt):
    enemies[len(enemies)] = Enemy()


@window.event
def on_mouse_motion(x, y, dx, dy):
    global mouse_pos
    mouse_pos = (x, y)


@window.event
def on_draw():
    window.clear()
    draw_enemies()


def start(w=640, h=480):
    gl.glClearColor(1.0, 1.0, 1.0, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    global width, height
    width = w
    height = h

    window.set_size(w, h)

    for i in range(1):
        enemies[i] = Enemy()

    pyglet.clock.schedule_interval(update, 1 / 144)
    pyglet.clock.schedule_interval(spawn_enemy, 0.5)
    pyglet.app.run()

start()
