import math
import random
from ctypes import *

import noise
import numpy
import pyglet
from pyglet.gl import *
from pyglet.window import key

from get_time import *

# from gl_shader import Shader

time = Time()

chunks = {}
active_chunks = set()

chunk_size = 16
height_multiplier = 30
zoom = 100
render_distance = 3

seed = random.uniform(-1000, 1000)

directions = ["left", "right", "bottom", "top", "front", "back"]

cube_signs = [
    [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)],   # Left      (-X)
    [(1, 0, 1), (1, 0, 0), (1, 1, 0), (1, 1, 1)],   # Right     (+X)
    [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],   # Bottom    (-Y)
    [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)],   # Top       (+Y)
    [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],   # Front     (-Z)
    [(1, 0, 0), (0, 0, 0), (0, 1, 0), (1, 1, 0)]    # Back      (+Z)
]

cube_normals = [
    (-1.0, 0.0, 0.0),
    (1.0, 0.0, 0.0),
    (0.0, -1.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, -1.0),
    (0.0, 0.0, 1.0)
]


def init():
    config_time(silent=True)

    glClearDepth(1.0)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthFunc(GL_LEQUAL)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glShadeModel(GL_SMOOTH)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glEnable(GL_CULL_FACE)

    global window, keys, texture
    window = CameraWindow()
    keys = key.KeyStateHandler()
    window.push_handlers(keys)

    texture = pyglet.resource.texture("images/dirt.png").get_texture()

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    pyglet.app.run()


class VBO:
    def __init__(self):
        self.vertex_buffer_set = False
        self.color_buffer_set = False
        self.normal_buffer_set = False
        self.texture_buffer_set = False

        self.buffer_vertex = GLuint(0)
        self.buffer_color = GLuint(0)
        self.buffer_normal = GLuint(0)
        self.buffer_texture_coords = GLuint(0)
        self.buffer_texture = GLuint(0)

        self.vertex_count = 0

        glGenBuffers(1, self.buffer_vertex)
        glGenBuffers(1, self.buffer_color)
        glGenBuffers(1, self.buffer_normal)
        glGenBuffers(1, self.buffer_texture_coords)
        glGenTextures(0, byref(self.buffer_texture))

    def data(self, data, buffer_type):
        if buffer_type == "vertex":
            self.vertex_buffer_set = True
            self.vertex_count = int(len(data) / 3)

            glBindBuffer(GL_ARRAY_BUFFER, self.buffer_vertex)

        elif buffer_type == "color":
            self.color_buffer_set = True
            glBindBuffer(GL_ARRAY_BUFFER, self.buffer_color)

        elif buffer_type == "normal":
            self.normal_buffer_set = True
            glBindBuffer(GL_ARRAY_BUFFER, self.buffer_normal)

        elif buffer_type == "texture":
            self.texture_buffer_set = True
            glBindTexture(data.target, data.id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 16, 16, 0, GL_RGB, GL_UNSIGNED_BYTE, data.get_image_data().get_data("RGB", 16 * 3))
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            return

        elif buffer_type == "texture_coords":
            glBindBuffer(GL_ARRAY_BUFFER, self.buffer_texture_coords)

        glBufferData(GL_ARRAY_BUFFER, len(data) * 4, to_gl_float(data), GL_DYNAMIC_DRAW)

    def vertex(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_vertex)
        glVertexPointer(3, GL_FLOAT, 0, 0)

    def color(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_color)
        glColorPointer(4, GL_FLOAT, 0, 0)

    def normal(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_normal)
        glNormalPointer(GL_FLOAT, 0, 0)

    def texture(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_texture_coords)
        glTexCoordPointer(3, GL_FLOAT, 0, 0)

    def draw(self):
        if self.vertex_buffer_set:
            glEnableClientState(GL_VERTEX_ARRAY)
            self.vertex()

        if self.color_buffer_set:
            glEnableClientState(GL_COLOR_ARRAY)
            self.color()

        if self.normal_buffer_set:
            glEnableClientState(GL_NORMAL_ARRAY)
            self.normal()

        if self.texture_buffer_set:
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(texture.target, texture.id)
            self.texture()

        glDrawArrays(GL_QUADS, 0, self.vertex_count)


# noinspection PyUnusedLocal
class Camera(object):
    x, y, z = 0, height_multiplier * 2, 0
    rx, ry = 340, 0
    w, h = 1920, 1080
    far = 8192
    fov = 90

    vx, vy, vz = 0, 0, 0

    speed_mult = 5
    camera_height = 2
    range = 5

    world_pos = None
    current_chunk = None
    current_tile = None
    direction = None

    modelview = None

    last_hit = None
    last_hit_color = None

    flying = False

    def view(self, width, height):
        self.w, self.h = width, height
        glViewport(0, 0, width, height)
        self.perspective()

    def perspective(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.w / self.h, 0.1, self.far)
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
            self.vx -= math.sin(math.radians(self.ry)) * self.speed_mult * dt
            self.vz -= math.cos(math.radians(self.ry)) * self.speed_mult * dt

            if self.flying:
                self.y += math.sin(math.radians(self.rx)) * self.speed_mult * dt

        elif keys[key.S]:
            self.vx += math.sin(math.radians(self.ry)) * self.speed_mult * dt
            self.vz += math.cos(math.radians(self.ry)) * self.speed_mult * dt

            if self.flying:
                self.y -= math.sin(math.radians(self.rx)) * self.speed_mult * dt

        if keys[key.D]:
            self.vx += math.cos(math.radians(self.ry)) * self.speed_mult * dt
            self.vz -= math.sin(math.radians(self.ry)) * self.speed_mult * dt

        elif keys[key.A]:
            self.vx -= math.cos(math.radians(self.ry)) * self.speed_mult * dt
            self.vz += math.sin(math.radians(self.ry)) * self.speed_mult * dt

    def key_down(self, symbol, modifiers):
        if symbol == key.F:
            self.flying = not self.flying

        elif symbol == key.ESCAPE:
            time.get("average")
            time.get("max")
            time.get("min")

            get_function_avg()

            pyglet.app.exit()

    def mouse_click(self, x, y, button, modifiers):
        pass

    def mouse_drag(self, x, y, dx, dy, buttons, modifers):
        self.mouse_move(x, y, dx, dy)

    def mouse_move(self, x, y, dx, dy):
        self.ry -= dx / 4

        if self.ry < 0:
            self.ry += 360

        if self.ry > 360:
            self.ry -= 360

        new_rx = self.rx + dy / 4

        if new_rx < 0:
            new_rx += 360

        if new_rx > 360:
            new_rx -= 360

        if 0 <= new_rx <= 90 or 270 <= new_rx <= 360:
            self.rx = new_rx

    def get_world_pos(self):
        modelview = to_gl_float([0] * 16)
        glGetFloatv(GL_MODELVIEW_MATRIX, modelview)
        self.modelview = [[modelview[w + h * 4] for w in range(4)] for h in range(4)]

        self.world_pos = numpy.dot([0, 0, 0, 1], numpy.linalg.inv(self.modelview))[:3]
        self.current_chunk, self.current_tile = get_chunk_pos(self.world_pos)

    def hitscan(self):
        for offset in range(-1, -self.range, -1):
            checking_pos = numpy.dot([0, 0, offset, 1], numpy.linalg.inv(self.modelview))
            checking_chunk, checking_tile = get_chunk_pos(checking_pos)

            if checking_chunk in active_chunks and checking_tile in chunks[checking_chunk].blocks:
                if chunks[checking_chunk].blocks[checking_tile]['position'][1] >= round(checking_pos[1]):
                    return checking_chunk, checking_tile

    def update(self, dt):
        self.get_world_pos()

        try:
            self.key_loop(dt)
        except NameError:
            pass

        if not self.flying and self.current_chunk in active_chunks and self.current_tile in chunks[self.current_chunk].blocks:
            height_diff = self.y - chunks[self.current_chunk].blocks[self.current_tile]['position'][1] - self.camera_height - 1

            if abs(height_diff) < 0.01:
                self.vy = 0

                if keys[key.SPACE]:
                    self.vy += 10

            elif height_diff > 0:
                self.vy -= 9.82 * dt

            elif height_diff < 0:
                self.y -= height_diff * 0.3
                self.vy = 0
        else:
            self.vy = 0

        self.x += self.vx
        self.y += self.vy * dt
        self.z += self.vz

        self.vx = 0
        self.vz = 0

    def apply(self):
        glLoadIdentity()
        glRotatef(-self.rx, 1, 0, 0)
        glRotatef(-self.ry, 0, 1, 0)
        glTranslatef(-self.x, -self.y, -self.z)


class Chunk:
    def __init__(self, pos):
        self.pos = pos
        self.cx, self.cz = pos

        self.vbo = VBO()
        self.blocks = {}

        self.is_meshed = False

    def generate(self):
        for sx in range(chunk_size):
            for sz in range(chunk_size):
                x = sx + self.pos[0] * chunk_size
                z = sz + self.pos[1] * chunk_size

                noise_height = noise.snoise3(x / zoom, z / zoom, seed, octaves=3)
                height = round((noise_height + 1) * height_multiplier)

                cube_color = None

                if -1.0 <= noise_height < -0.33:
                    cube_color = (0.0, 0.0, 0.5, 1.0)
                elif -0.33 <= noise_height < -0.11:
                    cube_color = (0.76, 0.70, 0.50, 1.0)
                elif -0.11 <= noise_height < 0.66:
                    cube_color = (0.0, 0.5, 0.0, 1.0)
                elif 0.66 <= noise_height <= 1.0:
                    cube_color = (0.8, 0.8, 0.8, 1.0)

                '''
                for y in range(height):
                    self.blocks[(sx, y, sz)] = {
                        'position': (sx, y, sz),
                        'world_pos': (x, y, z),
                        'color': cube_color
                    }
                '''

                self.blocks[(sx, sz)] = {
                    'position': (sx, height, sz),
                    'world_pos': (x, height, z),
                    'color': cube_color
                }

    def mesh(self):
        c_vertices = []
        c_colors = []
        c_normals = []
        c_textures = []

        for gx in [-1, 0, 1]:
            for gz in [-1, 0, 1]:
                chunk_pos = (self.cx + gx, self.cz + gz)

                if chunk_pos != self.pos and chunk_pos not in chunks:
                    chunks[chunk_pos] = Chunk(chunk_pos)
                    chunks[chunk_pos].generate()

        for block in self.blocks.values():
            x, y, z = block['world_pos']
            sx, sy, sz = block['position']

            arguments = (block['color'], c_vertices, c_colors, c_normals, c_textures)

            add_face((x, y, z), 'top', (1.0, 1.0, 1.0), *arguments)

            tests = [sx > 0, sx < chunk_size - 1, sz > 0, sz < chunk_size - 1]

            values = [(sx - 1, sz), (sx + 1, sz), (sx, sz - 1), (sx, sz + 1)]
            values2 = [(self.cx - 1, self.cz), (self.cx + 1, self.cz), (self.cx, self.cz - 1), (self.cx, self.cz + 1)]
            values3 = [(chunk_size - 1, sz), (0, sz), (sx, chunk_size - 1), (sx, 0)]

            faces = ['left', 'right', 'back', 'front']

            for i, test in enumerate(tests):
                if test:
                    test_height = self.blocks[values[i]]['position'][1]
                    height_diff = sy - test_height

                    if height_diff > 0:
                        add_face((x, (y + 1) - height_diff, z), faces[i], (1.0, height_diff, 1.0), *arguments)
                else:
                    test_height = chunks[values2[i]].blocks[values3[i]]['position'][1]
                    height_diff = sy - test_height

                    if height_diff > 0:
                        add_face((x, (y + 1) - height_diff, z), faces[i], (1.0, height_diff, 1.0), *arguments)

        self.vbo.data(c_vertices, "vertex")
        self.vbo.data(c_colors, "color")
        self.vbo.data(c_normals, "normal")
        self.vbo.data(texture, "texture")
        self.vbo.data(c_textures, "texture_coords")

        self.is_meshed = True

    def get_color(self, tile):
        self.vbo.color()

        data = to_gl_float([0] * 4)
        glGetBufferSubData(GL_ARRAY_BUFFER, (tile[0] * chunk_size + tile[1]) * 384, 16, data)
        return list(data)

    def set_color(self, tile, color):
        self.vbo.color()

        data = to_gl_float([*color] * 96)
        glBufferSubData(GL_ARRAY_BUFFER, (tile[0] * chunk_size + tile[1]) * 384, 384, data)

    def change_height(self, tile, height_diff):
        tile_height = self.blocks[tile]['position'][1]
        cube_size = 72 * sizeof(c_float)

        self.vbo.vertex()

        tile_data = to_gl_float([0] * cube_size)
        glGetBufferSubData(GL_ARRAY_BUFFER, (tile[0] * chunk_size + tile[1]) * cube_size, cube_size, tile_data)

        new_data = to_gl_float([c + height_diff if c == tile_height else c for c in tile_data])
        glBufferSubData(GL_ARRAY_BUFFER, (tile[0] * chunk_size + tile[1]) * cube_size, cube_size, new_data)

        self.blocks[tile]['position'][1] += height_diff
        self.blocks[tile]['world_pos'][1] += height_diff


# noinspection PyCallingNonCallable
def to_gl_float(data):
    return (GLfloat * len(data))(*data)


def get_chunk_pos(pos):
    chunk = (int(math.floor(pos[0] / chunk_size)), int(math.floor(pos[2] / chunk_size)))
    tile = (int(pos[0] - chunk[0] * chunk_size), int(pos[2] - chunk[1] * chunk_size))

    return chunk, tile


def add_cube(pos, scale, color, verts, cols, norms, texts):
    w, h, d = scale

    tex_coords = [
        (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, -h, 0.0), (0.0, -h, 0.0),       # Left
        (h, 0.0, 0.0), (h, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0),         # Right
        (1.0, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0),     # Bottom
        (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0),     # Top
        (0.0, 0.0, 1.0), (1.0, 0.0, 1.0), (1.0, h, 1.0), (0.0, h, 1.0),         # Front
        (1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, h, 0.0), (1.0, h, 0.0)          # Back
    ]

    vertices = []
    colors = []
    normals = []
    texture_coordinates = []

    for i, (sx, sy, sz) in enumerate(cube_signs):
        vertices.extend([pos[0] + (w * sx), pos[1] + (h * sy), pos[2] + (d * sz)])
        colors.extend([*color])
        normals.extend([*cube_normals[i // 4]])
        texture_coordinates.extend([*tex_coords[i]])

    verts.extend(vertices)
    cols.extend(colors)
    norms.extend(normals)
    texts.extend(texture_coordinates)


def add_face(pos, direction, scale, color, verts, cols, norms, texts):
    direction_index = directions.index(direction)

    x, y, z = pos
    w, h, d = scale
    
    tex_coords = [
        [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, -h, 0.0), (0.0, -h, 0.0)],       # Left
        [(h, 0.0, 0.0), (h, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0)],         # Right
        [(1.0, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)],     # Bottom
        [(0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)],     # Top
        [(0.0, 0.0, 1.0), (1.0, 0.0, 1.0), (1.0, h, 1.0), (0.0, h, 1.0)],         # Front
        [(1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, h, 0.0), (1.0, h, 0.0)]          # Back
    ]

    vertices = []
    colors = []
    normals = []
    texture_coordinates = []

    for i, (sx, sy, sz) in enumerate(cube_signs[direction_index]):
        vertices.extend([x + (w * sx), y + (h * sy), z + (d * sz)])
        colors.extend([*color])
        normals.extend([*cube_normals[direction_index]])
        texture_coordinates.extend([*tex_coords[direction_index][i]])

    verts.extend(vertices)
    cols.extend(colors)
    norms.extend(normals)
    texts.extend(texture_coordinates)


def render_light(pos, direction, angle, attenuation=0):
    glLightfv(GL_LIGHT0, GL_AMBIENT, to_gl_float((0.2, 0.2, 0.2, 1.0)))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, to_gl_float((1.0, 1.0, 1.0, 1.0)))
    glLightfv(GL_LIGHT0, GL_SPECULAR, to_gl_float((0.5, 0.5, 0.5, 1.0)))

    glLightfv(GL_LIGHT0, GL_POSITION, to_gl_float((*pos, attenuation)))
    glLightfv(GL_LIGHT0, GL_SPOT_CUTOFF, to_gl_float([angle]))
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, to_gl_float(direction))

    glEnable(GL_LIGHT0)


def check_draw_distance():
    current_chunk = window.cam.current_chunk
    active_chunks.clear()

    for cx in range(current_chunk[0] - render_distance, current_chunk[0] + render_distance + 1):
        for cz in range(current_chunk[1] - render_distance, current_chunk[1] + render_distance + 1):
            pos = (cx, cz)

            if pos not in chunks:
                chunks[pos] = Chunk(pos)
                chunks[pos].generate()
                chunks[pos].mesh()

            elif not chunks[pos].is_meshed:
                chunks[pos].mesh()

            active_chunks.add((cx, cz))


class CameraWindow(pyglet.window.Window):
    def __init__(self):
        super(CameraWindow, self).__init__(resizable=True)
        self.maximize()
        self.set_fullscreen()

        self.set_exclusive_mouse(True)

        self.cam = Camera()
        self.on_resize = self.cam.view
        self.on_key_press = self.cam.key_down
        self.on_mouse_press = self.cam.mouse_click
        self.on_mouse_drag = self.cam.mouse_drag
        self.on_mouse_motion = self.cam.mouse_move

        self.cam.update(0.0)

        pyglet.clock.schedule_interval(self.cam.update, 1 / 60)

    def on_draw(self):
        assert glGetError() == GL_NO_ERROR

        glClearColor(0.5, 0.69, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.cam.apply()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        render_light((0, 100, 0), (0.4, -0.824, 0.4), 45)

        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)

        check_draw_distance()

        for chunk in active_chunks:
            chunks[chunk].vbo.draw()

init()
