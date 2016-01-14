import random

import pyglet
import pyglet.gl as gl
from pyglet.window import key

from math import sin, cos, radians

height = 0
width = 0
target_scale = 10

target = set()

ball_batch = pyglet.graphics.Batch()
target_batch = pyglet.graphics.Batch()
paddle_batch = pyglet.graphics.Batch()

window = pyglet.window.Window()

ball = None
paddle = None
paddle_moving = None


class Ball:
    def __init__(self):
        self.x = width // 2
        self.y = 15
        self.radius = 5
        self.speed = [100, 100]
        self.color = (1, 0, 0)

    def draw(self):
        global ball_batch
        ball_batch = pyglet.graphics.Batch()

        draw_circle(round(self.x), round(self.y), self.radius, self.color)

    def move(self, dt):
        self.x += self.speed[0] * dt
        self.y += self.speed[1] * dt

        wall_detect()
        paddle_detect()


class Paddle:
    def __init__(self):
        self.x = width // 2
        self.y = 5
        self.color = (0, 1, 0)
        self.height = 5
        self.width = 100
        self.speed = 5

    def draw(self):
        global paddle_batch
        paddle_batch = pyglet.graphics.Batch()

        draw_rect(self.x, self.y, self.color, self.width, self.height, paddle_batch)

    def move(self, direction):
        if direction == "left":
            if self.x >= self.speed:
                self.x -= self.speed
            else:
                self.x = 0
        else:
            if width - (self.x + self.width) >= self.speed:
                self.x += self.speed
            else:
                self.x = width - self.width


def draw_rect(x, y, c, w, h, batch):
    r, g, b = c

    batch.add(4, gl.GL_QUADS, None,
              ('v2f', (x, y,
                       x + w, y,
                       x + w, y + h,
                       x, y + h)),
              ('c3f', (r, g, b, r, g, b, r, g, b, r, g, b)))


def draw_circle(x, y, r, c, tolerance=0.3):
    [draw_rect(x, y, c, 1, 1, ball_batch) for x, y in [(cx, cy) for cx in range(x - r, x + r + 1) for cy in range(y - r, y + r + 1) if r - (abs(x - cx) ** 2 + abs(y - cy) ** 2) ** 0.5 >= tolerance]]


def create_target(w=100, h=50):
    [target.add((x + (width - w) // 2, y + height - h - 20)) for y in range(0, h, target_scale) for x in range(0, w, target_scale) if random.random() > 0.5]


def draw_target():
    global target_batch
    target_batch = pyglet.graphics.Batch()

    for x, y in target:
        draw_rect(x, y, (0, 0, 0), target_scale, target_scale, target_batch)


def wall_detect():
    if ball.x <= ball.radius or width - ball.x <= ball.radius:
        ball.speed[0] *= -1

    if height - ball.y <= ball.radius:
        ball.speed[1] *= -1


def paddle_detect():
    if 0 <= ball.x - paddle.x <= paddle.width and ball.y - ball.radius <= paddle.y + paddle.height:
        relative_intersect = -1 * abs(ball.x - (paddle.x + paddle.width / 2))
        normalized_intersect = relative_intersect / (paddle.width / 2)
        bounce_angle = normalized_intersect * radians(75)

        ball.speed[0] = 100 * sin(bounce_angle)
        ball.speed[1] = 100 * cos(bounce_angle)


@window.event
def on_key_press(symbol, modifers):
    global paddle_moving

    if symbol == key.LEFT:
        paddle_moving = "left"

    elif symbol == key.RIGHT:
        paddle_moving = "right"


@window.event
def on_key_release(symbol, modifers):
    global paddle_moving

    if paddle_moving is not None:
        if symbol == key.LEFT and paddle_moving == "left":
            paddle_moving = None
        elif symbol == key.RIGHT and paddle_moving == "right":
            paddle_moving = None


@window.event
def on_draw():
    window.clear()

    ball.draw()

    ball_batch.draw()
    target_batch.draw()
    paddle_batch.draw()


def update(dt):
    ball.move(dt)

    if paddle_moving is not None:
        paddle.move(paddle_moving)
        paddle.draw()


def start(w=640, h=480):
    gl.glClearColor(1.0, 1.0, 1.0, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    global width, height, ball, paddle
    width = w
    height = h

    window.set_size(w, h)

    create_target()
    draw_target()

    ball = Ball()
    ball.draw()

    paddle = Paddle()
    paddle.draw()

    pyglet.clock.schedule_interval(update, 1 / 60)

    pyglet.app.run()

start()
