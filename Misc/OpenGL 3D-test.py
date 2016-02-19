import math
import random

import noise
import numpy
import pyglet
from pyglet.gl import *
from pyglet.window import key

fps_display = pyglet.clock.ClockDisplay()

chunks = {}
chunk_height = {}
active_chunks = set()

chunk_size = 10
height_multiplier = 30
zoom = 100
render_distance = 5

seed = random.uniform(-1000, 1000)

cube_signs = [
    (-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1),         # Top
    (-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1),     # Bottom
    (-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1),     # Left
    (1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1),         # Right
    (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),         # Front
    (1, -1, -1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1)      # Back
]

cube_normals = [
    (0.0, 1.0, 0.0),      # Top
    (0.0, -1.0, 0.0),     # Bottom
    (-1.0, 0.0, 0.0),     # Left
    (1.0, 0.0, 0.0),      # Right
    (0.0, 0.0, -1.0),     # Front
    (0.0, 0.0, 1.0)       # Back
]


def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClearDepth(1.0)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthFunc(GL_LEQUAL)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glShadeModel(GL_SMOOTH)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)


class VBO:
    def __init__(self):
        self.vertex_buffer_set = False
        self.color_buffer_set = False
        self.normal_buffer_set = False

        self.buffer_vertex = GLuint(0)
        self.buffer_color = GLuint(0)
        self.buffer_normal = GLuint(0)

        glGenBuffers(1, self.buffer_vertex)
        glGenBuffers(1, self.buffer_color)
        glGenBuffers(1, self.buffer_normal)

    def data(self, data, buffer_type):
        data_gl = to_gl_float(data)

        if buffer_type == "vertex":
            self.vertex_buffer_set = True
            glBindBuffer(GL_ARRAY_BUFFER, self.buffer_vertex)

        elif buffer_type == "color":
            self.color_buffer_set = True
            glBindBuffer(GL_ARRAY_BUFFER, self.buffer_color)

        elif buffer_type == "normal":
            self.normal_buffer_set = True
            glBindBuffer(GL_ARRAY_BUFFER, self.buffer_normal)

        glBufferData(GL_ARRAY_BUFFER, len(data) * 4, data_gl, GL_STATIC_DRAW)

    def vertex(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_vertex)
        glVertexPointer(3, GL_FLOAT, 0, 0)

    def color(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_color)
        glColorPointer(4, GL_FLOAT, 0, 0)

    def normal(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_normal)
        glNormalPointer(GL_FLOAT, 0, 0)

    def draw(self):
        if self.vertex_buffer_set:
            self.vertex()
        if self.color_buffer_set:
            self.color()
        if self.normal_buffer_set:
            self.normal()

        glDrawArrays(GL_QUADS, 0, chunk_size ** 2 * 24)


class Camera(object):
    x, y, z = 0, height_multiplier, 0
    rx, ry = 0, 0
    w, h = 1920, 1080
    far = 8192
    fov = 90

    speed_mult = 5
    world_pos = None
    current_chunk = None
    current_tile = None

    def view(self, width, height):
        self.w, self.h = width, height
        glViewport(0, 0, width, height)
        self.perspective()

    def perspective(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, float(self.w) / self.h, 0.1, self.far)
        glMatrixMode(GL_MODELVIEW)

    def key_loop(self, dt):
        if keys[key.LSHIFT]:
            self.speed_mult = 25
        else:
            self.speed_mult = 5

        if keys[key.NUM_SUBTRACT]:
            self.fov -= self.speed_mult * dt
            self.perspective()

        elif keys[key.NUM_ADD]:
            self.fov += self.speed_mult * dt
            self.perspective()

        if keys[key.W]:
            self.x -= math.sin(math.radians(self.ry)) * self.speed_mult * dt
            self.y += math.sin(math.radians(self.rx)) * self.speed_mult * dt
            self.z -= math.cos(math.radians(self.ry)) * self.speed_mult * dt

        elif keys[key.S]:
            self.x += math.sin(math.radians(self.ry)) * self.speed_mult * dt
            self.y -= math.sin(math.radians(self.rx)) * self.speed_mult * dt
            self.z += math.cos(math.radians(self.ry)) * self.speed_mult * dt

        if keys[key.D]:
            self.x += math.cos(math.radians(self.ry)) * self.speed_mult * dt
            self.z -= math.sin(math.radians(self.ry)) * self.speed_mult * dt

        elif keys[key.A]:
            self.x -= math.cos(math.radians(self.ry)) * self.speed_mult * dt
            self.z += math.sin(math.radians(self.ry)) * self.speed_mult * dt

    def drag(self, x, y, dx, dy, button, modifiers):
        if button == 4:
            self.ry -= dx / 4
            self.rx += dy / 4

            if self.rx < 0:
                self.rx += 360

            if self.ry < 0:
                self.ry += 360

    def apply(self):
        glLoadIdentity()
        glRotatef(-self.rx, 1, 0, 0)
        glRotatef(-self.ry, 0, 1, 0)
        glTranslatef(-self.x, -self.y, -self.z)

        modelview = to_gl_float([0] * 16)
        glGetFloatv(GL_MODELVIEW_MATRIX, modelview)
        self.world_pos = numpy.dot([0, 0, 0, 1], numpy.linalg.inv([[modelview[w + h * 4] for w in range(4)] for h in range(4)]))[:3]

        self.get_current_tile()

    def get_current_tile(self):
        self.current_chunk = (int(math.floor(self.world_pos[0] / chunk_size)), int(math.floor(self.world_pos[2] / chunk_size)))
        self.current_tile = (int(self.world_pos[0] - self.current_chunk[0] * chunk_size), int(self.world_pos[2] - self.current_chunk[1] * chunk_size))


def to_gl_float(data):
    return (GLfloat * len(data))(*data)


def generate_chunk(cx, cz):
    c_vertices = []
    c_colors = []
    c_normals = []

    chunk_height[(cx, cz)] = {}

    for sx in range(chunk_size):
        for sz in range(chunk_size):
            x = sx + cx * chunk_size
            z = sz + cz * chunk_size
            cube_height = noise.snoise3(x / zoom, z / zoom, seed, octaves=3)
            cube_color = None

            chunk_height[(cx, cz)][(sx, sz)] = cube_height

            if -1.0 <= cube_height < -0.33:
                cube_color = (0.0, 0.0, 1.0, 1.0)
            elif -0.33 <= cube_height < 0.33:
                cube_color = (0.0, 1.0, 0.0, 1.0)
            elif 0.33 <= cube_height <= 1.0:
                cube_color = (1.0, 0.0, 0.0, 1.0)

            add_cube((x, round(cube_height * height_multiplier), z), (1.0, 1.0, 1.0), cube_color, c_vertices, c_colors, c_normals)

    chunks[(cx, cz)] = VBO()
    chunks[(cx, cz)].data(c_vertices, "vertex")
    chunks[(cx, cz)].data(c_colors, "color")
    chunks[(cx, cz)].data(c_normals, "normal")


def add_cube(pos, scale, color, verts, cols, norms):
    x, y, z = pos
    w, h, d = scale[0] / 2, scale[1] / 2, scale[2] / 2
    r, g, b, a = color

    vertices = []
    colors = []
    normals = []

    index = 0

    for sx, sy, sz in cube_signs:
        vertices.extend([x + (w * sx), y + (h * sy), z + (d * sz)])
        colors.extend([r, g, b, a])
        normals.extend([*cube_normals[index // 4]])

        index += 1

    verts.extend(vertices)
    cols.extend(colors)
    norms.extend(normals)


def render_light(pos, angle):
    glLightfv(GL_LIGHT0, GL_AMBIENT, to_gl_float((0.2, 0.2, 0.2, 1.0)))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, to_gl_float((1, 1, 1, 1.0)))
    glLightfv(GL_LIGHT0, GL_SPECULAR, to_gl_float((0.5, 0.5, 0.5, 1.0)))

    glLightfv(GL_LIGHT0, GL_POSITION, to_gl_float((*pos, 0)))
    glLightfv(GL_LIGHT0, GL_SPOT_CUTOFF, to_gl_float([angle]))
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, to_gl_float((0, -1, 0)))

    glEnable(GL_LIGHT0)


def check_draw_distance():
    current_chunk = window.cam.current_chunk
    active_chunks.clear()

    for cx in range(current_chunk[0] - render_distance, current_chunk[0] + render_distance + 1):
        for cz in range(current_chunk[1] - render_distance, current_chunk[1] + render_distance + 1):
            if (cx, cz) not in chunks:
                generate_chunk(cx, cz)
            active_chunks.add((cx, cz))


class CameraWindow(pyglet.window.Window):
    def __init__(self):
        super(CameraWindow, self).__init__(resizable=True)
        self.maximize()

        self.cam = Camera()
        self.on_resize = self.cam.view
        self.on_mouse_drag = self.cam.drag

        pyglet.clock.schedule_interval(self.cam.key_loop, 1 / 60)

    def on_draw(self):
        self.clear()
        self.cam.apply()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        render_light((0, 10, 0), 45)

        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        check_draw_distance()

        for chunk in active_chunks:
            chunks[chunk].draw()

init()
window = CameraWindow()

keys = key.KeyStateHandler()
window.push_handlers(keys)

pyglet.app.run()
