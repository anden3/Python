import math
import random
from time import time

import pyglet
import pyglet.gl as gl
from pyglet.window import key

width = 1280
height = 800

gravity = 10
air_resistance = 0.01
friction_coefficient = 0.03
fire_delay = 0.1

window = pyglet.window.Window()
keys = key.KeyStateHandler()
fps_display = pyglet.clock.ClockDisplay()

terrain = pyglet.graphics.Batch()
shell_batch = pyglet.graphics.Batch()
ui = pyglet.graphics.Batch()

debug = pyglet.graphics.Batch()

window.push_handlers(keys)

tank1 = None

line_x = [0, width]

x_values = set()
y_values = {
    0: height / 2 + 1,
    width: height / 2
}

angles = {}

tank_rects = [
    (0, 0, 30, 10)
]

cannon_rects = [
    (13, 0, 4, 15)
]

shells = []
labels = []

circle_cols = {}


class Tank:
    def __init__(self):
        self.x = random.randint(5, width - 16)
        self.y = y_values[self.x]

        self.vx = 100
        self.vy = -1

        self.width = 30
        self.height = 16
        self.mass = 35

        self.fuel = 300

        self.max_speed = 50
        self.max_angle = 60
        self.max_fuel = 300

        self.angle = 0
        self.cannon_angle = 90

        self.on_ground = False

        self.color = (0.0, 0.4, 0.1, 1.0)

        self.batch = pyglet.graphics.Batch()
        self.cannon_batch = pyglet.graphics.Batch()

        self.last_fire = 0

        self.draw()

    def move(self, dx, dy):
        tank1.draw_fuel()

        if self.fuel <= 0:
            return

        if dx != 0 and abs(self.vx) >= self.max_speed:
            dx = 0

        if dy != 0 and abs(self.vy) >= self.max_speed:
            dy = 0

        self.vx += dx * math.cos(math.radians(self.angle)) + dy * -math.sin(math.radians(self.angle))
        self.vy += dx * math.sin(math.radians(self.angle)) + dy * math.cos(math.radians(self.angle))

    def check_ground(self):
        x_vals = [self.x, self.x + self.width / 2, self.x + self.width]
        diffs = [self.y - y_values[round(x)] for x in x_vals if 0 <= x < width]
        min_diff = min(diffs)

        self.on_ground = min_diff <= 0

        if min_diff <= 0:
            self.y -= min_diff
            self.vy = 0

            for diff in diffs:
                diff -= min_diff

            if len(diffs) > 2:
                angle = math.degrees(math.atan2(diffs[0] - diffs[2], self.width))

                if angle < 0:
                    angle += 360

                self.cannon_angle += angle - self.angle
                self.angle = angle

    def get_normal(self):
        return self.mass * gravity * abs(math.cos(math.radians(180 - abs(self.angle - 180))))

    def update(self, dt):
        if self.vy < 0:
            if self.on_ground:
                self.vy = 0

        if self.vx > 0:
            if self.x == width - self.width:
                self.vx = 0

            elif self.x > width - self.width:
                self.vx = 0
                self.x -= self.x - (width - self.width)

        elif self.vx < 0:
            if self.x == 0:
                self.vx = 0

            elif self.x < 0:
                self.vx = 0
                self.x -= self.x

        if self.on_ground and self.vx != 0:
            if friction_coefficient * self.get_normal() > abs(self.vx):
                self.vx = 0
            else:
                self.vx -= (get_rotated_coords(friction_coefficient * self.get_normal() * math.copysign(1, self.vx), 0, self.angle)[0])
                self.vy += (get_rotated_coords(friction_coefficient * self.get_normal(), 0, self.angle)[1])

        if not self.on_ground and self.vx != 0:
            self.vx -= air_resistance * self.vx

        self.vy -= gravity

        if self.on_ground:
            self.fuel -= abs(self.vx * dt)

        self.x += self.vx * dt
        self.y += self.vy * dt

        self.check_ground()

        self.draw()

    def fire(self):
        now = time()

        if now - self.last_fire >= fire_delay:
            self.last_fire = now
            shells.append(Shell(self.x + cannon_rects[0][0] + (cannon_rects[0][2] / 2),
                                self.y + cannon_rects[0][1] + cannon_rects[0][3],
                                math.cos(math.radians(self.cannon_angle)),
                                math.sin(math.radians(self.cannon_angle))))

    def draw(self):
        for x, y, w, h in tank_rects:
            draw_rect(self.x + x, self.y + y, w, h, self.color, self.batch)

        for x, y, w, h in cannon_rects:
            draw_rect(self.x + x, self.y + y, w, h, self.color, self.cannon_batch)

    def draw_fuel(self):
        draw_rect(10, height - 50, 102, 10, (0.0, 0.0, 0.0, 1.0), ui)
        draw_rect(11, height - 49, round((self.fuel / self.max_fuel) * 100), 8, (1.0, 0.0, 0.0, 1.0), ui)

    def render(self):
        gl.glPushMatrix()

        gl.glTranslatef(self.x + self.width / 2, self.y + self.height / 2, 0)
        gl.glRotatef(self.angle, 0, 0, 1)
        gl.glTranslatef(-self.x - self.width / 2, -self.y - self.height / 2, 0)

        self.batch.draw()

        gl.glPopMatrix()

        gl.glPushMatrix()

        cx, cy, cw, ch = cannon_rects[0]

        gl.glTranslatef(self.x + cx + cw / 2, self.y + cy + ch / 2, 0)
        gl.glRotatef(self.cannon_angle - 90, 0, 0, 1)
        gl.glTranslatef(-self.x - cx - cw / 2, -self.y - cy, 0)

        self.cannon_batch.draw()

        gl.glPopMatrix()

        self.batch = pyglet.graphics.Batch()
        self.cannon_batch = pyglet.graphics.Batch()


class Shell:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y

        self.speed = 700

        self.vx = vx * self.speed
        self.vy = vy * self.speed

        self.explosion_radius = 20

        if len(circle_cols) <= 0:
            self.gen_circle()

    def gen_circle(self, tolerance=0.5):
        for x in range(-self.explosion_radius, self.explosion_radius + 1):
            start_y = None
            length = 0

            for y in range(-self.explosion_radius, self.explosion_radius + 1):
                if math.sqrt(x ** 2 + y ** 2) - self.explosion_radius <= tolerance:
                    if start_y is None:
                        start_y = y
                    length += 1
                else:
                    if start_y is not None:
                        circle_cols[x] = (start_y, length)
                        break

            if circle_cols.setdefault(x, None) is None:
                circle_cols[x] = (0, 0)

    def explode(self):
        for x in range(round(self.x - self.explosion_radius - 15), round(self.x + self.explosion_radius + 15)):
            if 0 <= x <= width - 1:
                if circle_cols.setdefault(round(x - self.x), None) is not None:
                    draw_rect(x, 0, 1, height, (0.529, 0.807, 0.921, 1.0), terrain)
                    y_values[x] -= circle_cols[round(x - self.x)][1]

        smooth_curve(begin=round(self.x - self.explosion_radius - 5), end=round(self.x + self.explosion_radius + 50))

        for x in range(round(self.x - self.explosion_radius - 15), round(self.x + self.explosion_radius + 15)):
            if 0 <= x <= width - 1:
                draw_rect(x, 0, 1, y_values[x], (0.470, 0.282, 0.0, 1.0), terrain)


def draw_shells(dt):
    global shell_batch
    shell_batch = pyglet.graphics.Batch()

    for shell in shells.copy():
        shell.vx -= air_resistance * shell.vx
        shell.vy -= gravity

        shell.x += shell.vx * dt
        shell.y += shell.vy * dt

        if not (0 <= shell.x < width) or y_values.setdefault(round(shell.x), None) is None:
            shells.remove(shell)
            continue

        if shell.y - (y_values[round(shell.x)]) < 0:
            shell.explode()

            shells.remove(shell)
            continue

        draw_rect(shell.x - 1, shell.y - 1, 3, 3, (0.0, 0.0, 0.0, 1.0), shell_batch)


def get_rotated_coords(x, y, angle):
    return x + (math.cos(math.radians(angle)) + math.sin(math.radians(angle))) - 1, y + (-math.sin(math.radians(angle)) + math.cos(math.radians(angle))) - 1


def draw_rect(x, y, sw, sh, c, batch):
    r, g, b, a = c

    batch.add(4, gl.GL_QUADS, None, (
        'v2f', (
            x, y,
            x + sw, y,
            x + sw, y + sh,
            x, y + sh
        )
    ), (
        'c4f', (
            r, g, b, a,
            r, g, b, a,
            r, g, b, a,
            r, g, b, a
        )
    ))


def midpoint_algorithm(min_y, max_y, step, iterations):
    for _ in range(iterations):
        line_x.sort()

        for i, x in enumerate(line_x.copy()):
            if i < len(line_x) - 1:
                midpoint = x + abs(x - line_x[i + 1]) / 2

                if midpoint not in line_x and midpoint < width - 1:
                    line_x.append(midpoint)
                    y_values[midpoint] = y_values[x] + random.uniform(min_y, max_y)

        min_y /= step
        max_y /= step


def generate_heightmap(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    error = 0
    y = y0

    for x in range(round(x0), round(x1)):
        if x not in x_values:
            x_values.add(x)
            y_values[round(x)] = round(y)
            error += abs(dy / dx)

            while error >= 0.5:
                y += math.copysign(1, (y1 - y0))
                error -= 1


def print_lines():
    for i, x in enumerate(line_x):
        if i < len(line_x) - 1:
            generate_heightmap(x, y_values[x], line_x[i + 1], y_values[line_x[i + 1]])


def smooth_curve(begin=0, end=width, iterations=5, avg_range=5):
    for i in range(iterations):
        y_copy = y_values

        for x in range(begin, end):
            x1, x2 = x - avg_range, x + avg_range

            if x < avg_range:
                x1 = 0
            if x > width - avg_range - 1:
                x2 = width - 1

            avg_vals = [y_copy[cx] for cx in range(x1, x2)]

            if len(avg_vals) > 0:
                y_values[x] = round(sum(avg_vals) / len(avg_vals))


def line_fill():
    for x in x_values:
        draw_rect(x, 0, 1, y_values[x], (0.470, 0.282, 0.0, 1.0), terrain)


def draw_text():
    labels.append(pyglet.text.Label('Fuel', x=10, y=height - 30, color=(0, 0, 0, 255)))


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


@window.event
def on_draw():
    global debug

    window.clear()

    gl.glLoadIdentity()

    terrain.draw()
    ui.draw()

    tank1.render()
    shell_batch.draw()

    for label in labels:
        label.draw()

    fps_display.draw()

    debug.draw()
    debug = pyglet.graphics.Batch()


def check_keys():
    if keys[key.A]:
        tank1.move(-15, 0)
    elif keys[key.D]:
        tank1.move(15, 0)

    if keys[key.R]:
        tank1.fuel = tank1.max_fuel
        tank1.draw_fuel()

    if keys[key.LEFT]:
        tank1.cannon_angle += 1
    elif keys[key.RIGHT]:
        tank1.cannon_angle -= 1

    if keys[key.SPACE]:
        tank1.fire()

    if keys[key.Z]:
        global terrain
        terrain = pyglet.graphics.Batch()
        line_fill()


def game_loop(dt):
    check_keys()
    tank1.update(dt)
    draw_shells(dt)


def start():
    global tank1

    gl.glClearColor(0.529, 0.807, 0.921, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    window.set_size(width, height)
    window.maximize()
    x, y = window.get_location()
    window.set_location(x - 100, y)

    midpoint_algorithm(-50, 50, 1.3, 7)
    print_lines()
    smooth_curve()
    line_fill()

    draw_text()

    tank1 = Tank()

    # get_angles()

    pyglet.clock.schedule_interval(game_loop, 1 / 120)
    pyglet.app.run()


start()
