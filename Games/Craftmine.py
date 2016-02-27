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
height_multiplier = 64
render_distance = 3

zoom = 100

seed = random.uniform(-1000, 1000)

directions = ["left", "right", "bottom", "top", "front", "back"]

texture_pos = {
    "snow": (0, 0),
    "grass": (1, 0),
    "sand": (0, 1),
    "blue wool": (1, 1)
}

texture_color = {
    "snow": (0.8, 0.8, 0.8, 1.0),
    "grass": (0.0, 0.5, 0.0, 1.0),
    "sand": (0.76, 0.7, 0.5, 1.0),
    "blue wool": (0.0, 0.0, 0.5, 1.0)
}

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

texture_coords = [
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],   # Left
    [(1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 0)],   # Right
    [(1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0)],   # Bottom
    [(0, 1, 0), (0, 0, 0), (1, 0, 0), (1, 1, 0)],   # Top
    [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],   # Front
    [(1, 0, 0), (0, 0, 0), (0, 1, 0), (1, 1, 0)]    # Back
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

    images = [
        pyglet.image.load("images/snow.png").get_image_data(),
        pyglet.image.load("images/grass_top.png").get_image_data(),
        pyglet.image.load("images/sand.png").get_image_data(),
        pyglet.image.load("images/wool_colored_blue.png").get_image_data()
    ]

    texture_atlas = pyglet.image.atlas.TextureAtlas(width=32, height=32)

    for image in images:
        texture_atlas.add(image)

    texture = texture_atlas.texture

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    pyglet.app.run()


class VBO:
    def __init__(self):
        self.buffer_size = chunk_size ** 2 * height_multiplier * 24 * 2
        self.vertex_count = 0

        self.buffers = {
            "vertex": None,
            "color": None,
            "normal": None,
            "texture": None,
            "texture_coords": None
        }

        self.generate()

    def generate(self):
        for buffer in ["vertex", "color", "normal", "texture_coords"]:
            self.buffers[buffer] = GLuint(0)
            glGenBuffers(1, self.buffers[buffer])
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers[buffer])
            glBufferData(GL_ARRAY_BUFFER, self.buffer_size, None, GL_DYNAMIC_DRAW)

    def empty(self):
        for buffer in ["vertex", "color", "normal", "texture_coords"]:
            self.buffers[buffer] = GLuint(0)
            glGenBuffers(1, self.buffers[buffer])
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers[buffer])
            glBufferData(GL_ARRAY_BUFFER, self.buffer_size, None, GL_DYNAMIC_DRAW)

    def data(self, buffer_type, data, offset, increase_vertex=True):
        if buffer_type != "texture":
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers[buffer_type])

            if buffer_type == "color":
                offset *= 16
            else:
                offset *= 12

            gl_data = to_gl_float(data)
            glBufferSubData(GL_ARRAY_BUFFER, offset, sizeof(gl_data), gl_data)

            if buffer_type == "vertex" and increase_vertex:
                self.vertex_count += int(len(data) / 3)

        else:
            self.buffers[buffer_type] = GLuint(0)
            glGenTextures(1, self.buffers[buffer_type])
            glBindTexture(data.target, data.id)

            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, texture.width, texture.height, 0, GL_RGB, GL_UNSIGNED_BYTE,
                         data.get_image_data().get_data("RGB", texture.width * 3))
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    def vertex(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffers["vertex"])
        glVertexPointer(3, GL_FLOAT, 0, 0)

    def color(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffers["color"])
        glColorPointer(4, GL_FLOAT, 0, 0)

    def normal(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffers["normal"])
        glNormalPointer(GL_FLOAT, 0, 0)

    def texture(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffers["texture_coords"])
        glTexCoordPointer(3, GL_FLOAT, 0, 0)

    def draw(self):
        if self.buffers["vertex"] is not None:
            glEnableClientState(GL_VERTEX_ARRAY)
            self.vertex()

        if self.buffers["color"] is not None:
            glEnableClientState(GL_COLOR_ARRAY)
            self.color()

        if self.buffers["normal"] is not None:
            glEnableClientState(GL_NORMAL_ARRAY)
            self.normal()

        if self.buffers["texture_coords"] is not None:
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(texture.target, texture.id)
            self.texture()

        glDrawArrays(GL_QUADS, 0, self.vertex_count)


# noinspection PyUnusedLocal
class Camera(object):
    x, y, z = 0, height_multiplier, 0
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
            time.get("all")

            get_function_avg()

            pyglet.app.exit()

    def mouse_click(self, x, y, button, modifiers):
        hit = self.hitscan()

        if hit is not None and hit[0] is not None and hit[1] is not None:
            if button == 1:
                chunks[hit[0]].remove_block(hit[1])
            elif button == 4:
                chunks[hit[0]].create_block((hit[1][0], hit[1][1] + 1, hit[1][2]), new=True)
                # chunks[hit[0]].set_color(hit[1], (1.0, 1.0, 1.0, 1.0))

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

            sx, sy, sz = checking_tile

            if checking_chunk in active_chunks:
                if checking_tile in chunks[checking_chunk].blocks:
                    return checking_chunk, checking_tile
                else:
                    for x in [sx - 1, sx, sx + 1]:
                        for z in [sz - 1, sz, sz + 1]:
                            if x != sx and z != sz:
                                if (x, sy, z) in chunks[checking_chunk].blocks:
                                    return checking_chunk, (x, sy, z)

    def update(self, dt):
        self.get_world_pos()

        try:
            self.key_loop(dt)
        except NameError:
            pass

        if (not self.flying and self.current_chunk in active_chunks and
           (self.current_tile[0], self.current_tile[2]) in chunks[self.current_chunk].heightmap):
            height_diff = self.y - chunks[self.current_chunk].heightmap[(self.current_tile[0], self.current_tile[2])] - self.camera_height - 1

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
        self.cx, self.cz = pos

        self.vbo = VBO()
        self.heightmap = {}
        self.blocks = {}

        self.offset = 0

        self.is_meshed = False

    def generate(self):
        for sx in range(chunk_size):
            for sz in range(chunk_size):
                x = sx + self.cx * chunk_size
                z = sz + self.cz * chunk_size

                noise_height = noise.snoise3(x / zoom, z / zoom, seed, octaves=3)
                height = round((noise_height + 1) / 2 * height_multiplier)

                self.heightmap[(sx, sz)] = height

                texture_name = None

                if -1.0 <= noise_height < -0.33:
                    texture_name = "blue wool"

                elif -0.33 <= noise_height < -0.11:
                    texture_name = "sand"

                elif -0.11 <= noise_height < 0.66:
                    texture_name = "grass"

                elif 0.66 <= noise_height <= 1.0:
                    texture_name = "snow"

                for y in range(height - 2, height + 1):
                    self.blocks[(sx, y, sz)] = {
                        'texture': texture_name
                    }

    def mesh(self):
        if not self.is_meshed:
            for gx in [-1, 0, 1]:
                for gz in [-1, 0, 1]:
                    chunk_pos = (self.cx + gx, self.cz + gz)

                    if chunk_pos != (self.cx, self.cz) and chunk_pos not in chunks:
                        chunks[chunk_pos] = Chunk(chunk_pos)
                        chunks[chunk_pos].generate()

        self.vbo.data("texture", texture, 0)

        for pos in self.blocks.copy():
            self.create_block(pos)

        self.is_meshed = True

    def get_color(self, tile):
        self.vbo.color()
        offset = self.blocks[tile]['offset']

        data = to_gl_float([0] * 4)
        glGetBufferSubData(GL_ARRAY_BUFFER, offset * 16, 16, data)

        return list(data)

    def set_color(self, tile, color):
        offset = self.blocks[tile]['offset']
        length = bin(self.blocks[tile]['faces']).count('1')

        self.vbo.data("color", [*color] * length, offset)

    def create_block(self, tile, new=False):
        data = ([], [], [], [])
        data_names = ["vertex", "color", "normal", "texture_coords"]

        if self.add_block(tile, data, new=new):
            offset = self.blocks[tile]['offset']

            for i, data_list in enumerate(data):
                self.vbo.data(data_names[i], data_list, offset)

    def remove_block(self, tile):
        faces = self.blocks[tile]['faces']

        self.blocks.pop(tile)
        self.vbo = VBO()
        self.offset = 0

        x, y, z = tile

        neighbors = [
            (x - 1, y, z), (x + 1, y, z),
            (x, y - 1, z), (x, y + 1, z),
            (x, y, z - 1), (x, y, z + 1)
        ]

        for i, c in enumerate(bin(faces)[2:].zfill(6)[::-1]):
            # if c == '0':
                neighbor = neighbors[i]

                if not 0 <= neighbor[0] < chunk_size:
                    continue

                if not 0 <= neighbor[2] < chunk_size:
                    continue

                if neighbor[1] > self.heightmap[(neighbor[0], neighbor[2])]:
                    continue

                if neighbor not in self.blocks:
                    self.blocks[neighbor] = {
                        'texture': "grass"
                    }

                    if (neighbor[0], neighbor[2]) in self.heightmap:
                        if self.heightmap[(neighbor[0], neighbor[2])] < neighbor[1]:
                            self.heightmap[(neighbor[0], neighbor[2])] = neighbor[1]

        if self.heightmap[(tile[0], tile[2])] == tile[1]:
            self.heightmap[(tile[0], tile[2])] -= 1

        self.mesh()

    def add_block(self, tile, data, new=False):
        sx, sy, sz = tile

        x = sx + self.cx * chunk_size
        z = sz + self.cz * chunk_size

        if new:
            self.heightmap[(sx, sz)] = sy

            if (sx, sy - 1, sz) in self.blocks:
                texture_name = self.blocks[(sx, sy - 1, sz)]['texture']
            else:
                texture_name = "grass"

            self.blocks[(sx, sy, sz)] = {
                'texture': texture_name
            }
        else:
            texture_name = self.blocks[tile]['texture']

        self.blocks[(sx, sy, sz)]['faces'] = 0

        if sy == self.heightmap[(sx, sz)]:
            add_face((x, sy, z), 'top', texture_name, *data)
            self.blocks[(sx, sy, sz)]['faces'] += 2 ** 3

        tests = [
            sx > 0, sx < chunk_size - 1,
            sz > 0, sz < chunk_size - 1
        ]

        values = [
            (sx - 1, sz), (sx + 1, sz),
            (sx, sz - 1), (sx, sz + 1)
        ]
        values2 = [
            (self.cx - 1, self.cz), (self.cx + 1, self.cz),
            (self.cx, self.cz - 1), (self.cx, self.cz + 1)
        ]
        values3 = [
            (chunk_size - 1, sz), (0, sz),
            (sx, chunk_size - 1), (sx, 0)
        ]

        faces = ['left', 'right', 'back', 'front']

        for i, test in enumerate(tests):
            if test:
                height_diff = sy - self.heightmap[values[i]]
            else:
                height_diff = sy - chunks[values2[i]].heightmap[values3[i]]

            if height_diff > 0:
                add_face((x, sy, z), faces[i], texture_name, *data)
                self.blocks[(sx, sy, sz)]['faces'] += 2 ** directions.index(faces[i])

        if self.blocks[(sx, sy, sz)]['faces'] == 0:
            del self.blocks[(sx, sy, sz)]
            return False
        else:
            self.blocks[(sx, sy, sz)]['offset'] = self.offset
            self.offset += bin(self.blocks[(sx, sy, sz)]['faces']).count('1') * 4
            return True


def distance(p1, p2):
    assert len(p1) == len(p2)

    return math.sqrt(sum([(p2[i] - p1[i]) ** 2 for i in range(len(p1))]))


# noinspection PyCallingNonCallable
def to_gl_float(data):
    return (GLfloat * len(data))(*data)


def get_chunk_pos(pos):
    chunk = (int(math.floor(pos[0] / chunk_size)), int(math.floor(pos[2] / chunk_size)))
    tile = (int(pos[0] - chunk[0] * chunk_size), int(pos[1]), int(pos[2] - chunk[1] * chunk_size))

    return chunk, tile


def add_face(pos, direction, texture_name, verts, cols, norms, texts, scale=(1.0, 1.0, 1.0)):
    direction_index = directions.index(direction)

    x, y, z = pos
    w, h, d = scale
    texture_position = texture_pos[texture_name]

    texture_positions = [
        [(texture_position[0] * 16) / texture.width, (texture_position[1] * 16) / texture.height],
        [((texture_position[0] + 1) * 16) / texture.width, ((texture_position[1] + 1) * 16) / texture.height]
    ]

    vertices = []
    colors = []
    normals = []
    tex_coords = []

    for tx, ty, tz in texture_coords[direction_index]:
        tex_coords.append(texture_positions[tx][0])
        tex_coords.append(texture_positions[ty][1] * h)
        tex_coords.append(tz)

    for i, (sx, sy, sz) in enumerate(cube_signs[direction_index]):
        vertices.extend([x + (w * sx), y + (h * sy), z + (d * sz)])
        colors.extend([*texture_color[texture_name]])
        normals.extend([*cube_normals[direction_index]])

    verts.extend(vertices)
    cols.extend(colors)
    norms.extend(normals)
    texts.extend(tex_coords)


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

            active_chunks.add(pos)


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
