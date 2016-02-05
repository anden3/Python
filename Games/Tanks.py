import pyglet
import pyglet.gl as gl
# from pyglet.window import key

import random
import math

from time import perf_counter

width = 320
height = 240

window = pyglet.window.Window()

terrain = pyglet.graphics.Batch()

fps_display = pyglet.clock.ClockDisplay()

x_vals = set()

x_values = [0, width]
y_values = {
    0: height / 2 + 1,
    width: height / 2
}


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
        'c4f', (r, g, b, a, r, g, b, a, r, g, b, a, r, g, b, a)))


def midpoint_algorithm(min_y, max_y, step, iterations):
    for _ in range(iterations):
        x_values.sort()

        for i, x in enumerate(x_values.copy()):
            if i < len(x_values) - 1:
                midpoint = x + abs(x - x_values[i + 1]) / 2

                if midpoint not in x_values and midpoint < width - 1:
                    x_values.append(midpoint)
                    y_values[midpoint] = y_values[x] + random.uniform(min_y, max_y)

        min_y /= step
        max_y /= step


def bresenham(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    error = 0
    derr = abs(dy / dx)
    y = y0

    for x in range(round(x0), round(x1)):
        if x not in x_vals:
            x_vals.add(x)
            y_values[round(x)] = round(y)

            draw_rect(round(x), round(y), 1, 5, (0.0, 0.31372, 0.0, 1.0), terrain)
            error += derr

            while error >= 0.5:
                draw_rect(round(x), round(y), 1, 5, (0.0, 0.31372, 0.0, 1.0), terrain)
                y += math.copysign(1, (y1 - y0))
                error -= 1


def print_lines():
    for i, x in enumerate(x_values):
        if i < len(x_values) - 1:
            bresenham(x, y_values[x], x_values[i + 1], y_values[x_values[i + 1]])


def flood_fill():
    verts = []
    added_verts = set()
    count = 0
    rects = 0

    lowest_point = height

    for x in x_vals:
        if y_values[x] < lowest_point:
            lowest_point = y_values[x]

    draw_rect(0, 0, width, lowest_point, (0.470, 0.282, 0.0, 1.0), terrain)

    for x in x_vals:
        for y in range(lowest_point, y_values[x]):
            verts.append((x, y))

    for x, y in verts:
        count += 1
        print(str(count) + " of " + str(len(verts)))

        if (x, y) not in added_verts:
            cell_width = width - x
            cell_height = height - lowest_point - y

            while cell_width > 0 and cell_height > 0:
                fits = True

                for sy in range(y, y + cell_height):
                    for sx in range(x, x + cell_width):
                        if (sx, sy) not in verts:
                            fits = False
                            if (sx - 1, sy) in verts:
                                cell_width -= 1
                            elif (sx, sy - 1) in verts:
                                cell_height -= 1
                            else:
                                if cell_width > 1:
                                    cell_width -= 1
                                if cell_height > 1:
                                    cell_height -= 1
                            break

                    if not fits:
                        break
                if fits:
                    draw_rect(x, y, cell_width, cell_height, (0.470, 0.282, 0.0, 1.0), terrain)
                    break
            else:
                if cell_width > 1:
                    draw_rect(x, y, cell_width, 1, (0.470, 0.282, 0.0, 1.0), terrain)
                else:
                    draw_rect(x, y, 1, 1, (0.470, 0.282, 0.0, 1.0), terrain)

            rects += 1

            for vx in range(x, x + cell_width):
                for vy in range(y, y + cell_height):
                    added_verts.add((vx, vy))
    print(rects)


@window.event
def on_key_press(symbol, modifers):
    pass


@window.event
def on_draw():
    window.clear()
    terrain.draw()
    fps_display.draw()


def start():
    gl.glClearColor(0.529, 0.807, 0.921, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    window.set_size(width, height)
    # x, y = window.get_location()
    # window.set_location(x, y - 150)

    t1 = perf_counter()

    midpoint_algorithm(-50, 50, 1.3, 7)
    print_lines()
    flood_fill()

    print(str((perf_counter() - t1) * 1000) + " ms.") if perf_counter() - t1 < 1 else print(str(perf_counter() - t1) + " s.")

    pyglet.app.run()

start()
