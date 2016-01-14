import random

import pyglet
import pyglet.gl as gl
from pyglet.window import key

height = 0
width = 0
scale = 0

snake = None

pickup_pos = None

window = pyglet.window.Window()

snake_batch = pyglet.graphics.Batch()
pickup_batch = pyglet.graphics.Batch()


class Snake:
    def __init__(self):
        self.x = 50
        self.y = 50
        self.width = 10
        self.height = 10
        self.speed = 100
        self.length_diff = 0
        self.direction = "right"
        self.segments = [(i, 50) for i in range(150, 50, -1)]
        self.color = (0, 0, 0)

    def move(self, dt):
        if self.direction == "left":
            for i in range(round(self.speed * dt)):
                self.x -= 1
                self.segments.insert(0, (self.x, self.y))

                if self.length_diff <= 0:
                    self.segments.pop()
                else:
                    self.length_diff -= 1
        elif self.direction == "right":
            for i in range(round(self.speed * dt)):
                self.x += 1
                self.segments.insert(0, (self.x, self.y))

                if self.length_diff <= 0:
                    self.segments.pop()
                else:
                    self.length_diff -= 1
        elif self.direction == "up":
            for i in range(round(self.speed * dt)):
                self.y += 1
                self.segments.insert(0, (self.x, self.y))

                if self.length_diff <= 0:
                    self.segments.pop()
                else:
                    self.length_diff -= 1
        elif self.direction == "down":
            for i in range(round(self.speed * dt)):
                self.y -= 1
                self.segments.insert(0, (self.x, self.y))

                if self.length_diff <= 0:
                    self.segments.pop()
                else:
                    self.length_diff -= 1

        self.wall_detect()
        self.pickup_detect()

    def draw(self):
        global snake_batch
        snake_batch = pyglet.graphics.Batch()

        for x, y in self.segments:
            draw_rect(x, y, self.color, self.width, self.height, snake_batch)

    def wall_detect(self):
        if not (0 <= self.x <= width - 1) or not (0 <= self.y <= height - 1):
            pyglet.clock.unschedule(update)

    def pickup_detect(self):
        if abs((pickup_pos[0] + 5) - (self.x + 5)) <= 5 and abs((pickup_pos[1] + 5) - (self.y + 5)) <= 5:
            snake.length_diff += 20
            place_pickup()


def place_pickup():
    global pickup_batch, pickup_pos
    pickup_batch = pyglet.graphics.Batch()

    x = random.randint(0, width - 10)
    y = random.randint(0, height - 10)

    pickup_pos = (x, y)

    draw_rect(x, y, (1, 0, 0), 10, 10, pickup_batch)


def draw_rect(x, y, c, w, h, batch):
    r, g, b = c

    batch.add(4, gl.GL_QUADS, None,
              ('v2f', (x, y,
                       x + w, y,
                       x + w, y + h,
                       x, y + h)),
              ('c3f', (r, g, b, r, g, b, r, g, b, r, g, b)))


def update(dt):
    snake.move(dt)


@window.event
def on_draw():
    window.clear()
    snake.draw()

    snake_batch.draw()
    pickup_batch.draw()


@window.event
def on_key_press(symbol, modifers):
    if symbol == key.LEFT and snake.direction != "right":
        snake.direction = "left"
    elif symbol == key.RIGHT and snake.direction != "left":
        snake.direction = "right"
    elif symbol == key.UP and snake.direction != "down":
        snake.direction = "up"
    elif symbol == key.DOWN and snake.direction != "up":
        snake.direction = "down"


def start(w=640, h=480, s=10):
    gl.glClearColor(1.0, 1.0, 1.0, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    window.set_size(w, h)

    global width, height, scale, snake
    scale = s
    width = w
    height = h

    place_pickup()

    snake = Snake()

    pyglet.clock.schedule_interval(update, 1 / 60)

    pyglet.app.run()

start()
