import math
import random

import pyglet
import pyglet.gl as gl
from pyglet.window import key

width = 1280
height = 800

gravity = 10
air_resistance = 0.01
friction_coefficient = 0.03
grass_height = 5

window = pyglet.window.Window()
keys = key.KeyStateHandler()
fps_display = pyglet.clock.ClockDisplay()

terrain = pyglet.graphics.Batch()
ui = pyglet.graphics.Batch()

window.push_handlers(keys)

tank1, tank2 = None, None

line_x = [0, width]

x_values = set()
y_values = {
    0: height / 2 + 1,
    width: height / 2
}

tank_rects = [
    (0, 0, 20, 5)
    # (0, 0, 30, 10),
    # (12, 10, 6, 10)
]


class Tank:
    def __init__(self):
        self.x = random.randint(5, width - 16)
        self.y = y_values[self.x] + 300

        self.angle_pos_x = self.x
        self.angle_pos_y = self.y

        self.vx = 100
        self.vy = -1

        self.width = 20
        self.height = 5
        self.mass = 35

        self.fuel = 300

        self.max_speed = 50
        self.max_angle = 60
        self.max_fuel = 300

        self.angle = 0

        self.on_ground = False

        self.color = (0.0, 0.4, 0.1, 1.0)
        self.batch = pyglet.graphics.Batch()

        self.draw()

    def move(self, dx, dy):
        if self.fuel <= 0:
            return

        if dx != 0 and abs(self.vx) >= self.max_speed:
            dx = 0

        if dy != 0 and abs(self.vy) >= self.max_speed:
            dy = 0

        self.vx += dx * math.cos(math.radians(self.angle)) + dy * -math.sin(math.radians(self.angle))
        self.vy += dx * math.sin(math.radians(self.angle)) + dy * math.cos(math.radians(self.angle))

    def check_ground(self):
        for x, y in [(x + self.angle_pos_x, self.angle_pos_y - self.height) for x in range(self.width)]:
            draw_rect(x - 1, y - 1, 3, 3, (1.0, 0.0, 0.0, 1.0), self.batch)

            if 0 <= x < width:
                if y == y_values[round(x)]:
                    self.on_ground = True
                    break

                elif y < y_values[round(x)]:
                    if self.vx < 0 and 270 <= self.angle <= 360 - self.max_angle:
                        self.x += 1
                        self.vx = 0

                    elif self.vx > 0 and self.max_angle <= self.angle <= 90:
                        self.x -= 1
                        self.vx = 0

                    else:
                        self.y += (y_values[round(x)] - grass_height) - y

                    self.on_ground = True
                    break

                else:
                    self.on_ground = False

    def check_angle(self):
        if self.on_ground:
            if y_values.setdefault(round(self.angle_pos_x + self.width), None) is not None:
                x1, x2 = round(self.angle_pos_x), round(self.angle_pos_x + self.width)
                y1, y2 = y_values.setdefault(x1, None), y_values.setdefault(x2, None)

                if y1 is not None and y2 is not None:
                    if y1 != y2:
                        slope = (y2 - y1) / (x2 - x1)
                        angle = math.degrees(math.acos(self.width / math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)))

                        if slope < 0:
                            angle = 360 - angle

                        self.angle = angle
        else:
            self.angle = 0

    def get_normal(self):
        return self.mass * gravity * abs(math.cos(math.radians(180 - abs(self.angle - 180))))

    def update(self, dt):
        self.check_ground()
        self.check_angle()

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
            self.vx -= air_resistance * abs(self.vx) * math.copysign(1, self.vx)

        self.vy -= gravity

        if self.on_ground:
            self.fuel -= abs(self.vx * dt)

        self.x += self.vx * dt
        self.y += self.vy * dt

        self.draw()

    def draw(self):
        for x, y, w, h in tank_rects:
            draw_rect(self.x + x, self.y + y, w, h, self.color, self.batch)

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

        p1 = get_rotated_coords(0, 0, self.angle)
        self.angle_pos_x, self.angle_pos_y = self.x + p1[0], self.y + p1[1]

        self.batch = pyglet.graphics.Batch()


def get_rotated_coords(x, y, angle):
    return x + (math.cos(math.radians(angle)) + math.sin(math.radians(angle))) - 1, \
           y + (-math.sin(math.radians(angle)) + math.cos(math.radians(angle))) - 1


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


def bresenham(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    error = 0
    y = y0

    for x in range(round(x0), round(x1)):
        if x not in x_values:
            x_values.add(x)
            y_values[round(x)] = round(y)

            draw_rect(round(x), round(y), 1, grass_height, (0.0, 0.31372, 0.0, 1.0), terrain)
            error += abs(dy / dx)

            while error >= 0.5:
                draw_rect(round(x), round(y), 1, grass_height, (0.0, 0.31372, 0.0, 1.0), terrain)
                y += math.copysign(1, (y1 - y0))
                error -= 1


def print_lines():
    for i, x in enumerate(line_x):
        if i < len(line_x) - 1:
            bresenham(x, y_values[x], line_x[i + 1], y_values[line_x[i + 1]])


def line_fill():
    for x in x_values:
        draw_rect(x, 0, 1, y_values[x], (0.470, 0.282, 0.0, 1.0), terrain)


@window.event
def on_draw():
    window.clear()

    gl.glLoadIdentity()

    terrain.draw()
    ui.draw()
    fps_display.draw()

    tank1.render()
    # tank2.render()


def check_keys():
    if keys[key.A]:
        tank1.move(-15, 0)
    elif keys[key.D]:
        tank1.move(15, 0)

    elif keys[key.W]:
        tank1.move(0, 15)

    if keys[key.Q]:
        tank1.angle += 5
    elif keys[key.E]:
        tank1.angle -= 5

    if keys[key.R]:
        tank1.fuel = tank1.max_fuel


def game_loop(dt):
    check_keys()
    tank1.draw_fuel()
    tank1.update(dt)
    # tank2.update(dt)


def start():
    global tank1, tank2

    gl.glClearColor(0.529, 0.807, 0.921, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    window.set_size(width, height)
    window.maximize()
    x, y = window.get_location()
    window.set_location(x - 100, y)

    # midpoint_algorithm(-5, 5, 0.1, 2)
    midpoint_algorithm(-50, 50, 1.3, 7)
    print_lines()
    line_fill()

    tank1 = Tank()
    # tank2 = Tank()

    pyglet.clock.schedule_interval(game_loop, 1 / 120)

    pyglet.app.run()


start()
