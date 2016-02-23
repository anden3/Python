import math
import random
from ctypes import *

import noise
import numpy
import pyglet
from get_time import Time
from pyglet.gl import *
from pyglet.window import key

time = Time()

chunks = {}
chunk_height = {}
chunk_textures = {}
active_chunks = set()

chunk_size = 4
height_multiplier = 5
zoom = 100
render_distance = 3

seed = random.uniform(-1000, 1000)

textures = {
    "blue_wool": pyglet.resource.texture("images/wool_colored_blue.png").get_texture(),
    "sand": pyglet.resource.texture("images/sand.png").get_texture(),
    "grass": pyglet.resource.texture("images/grass_top.png").get_texture(),
    "snow": pyglet.resource.texture("images/snow.png").get_texture()
}

texture_data = {
    "blue_wool": textures["blue_wool"].get_image_data().get_data("RGB", 16 * 3),
    "sand": textures["sand"].get_image_data().get_data("RGB", 16 * 3),
    "grass": textures["grass"].get_image_data().get_data("RGB", 16 * 3),
    "snow": textures["snow"].get_image_data().get_data("RGB", 16 * 3)
}

generated_textures = {
    "blue_wool": False,
    "sand": False,
    "grass": False,
    "snow": False
}

texture_buffer = GLuint(0)
glGenTextures(3, byref(texture_buffer))


def bind_texture(name):
    if not generated_textures[name]:
        generated_textures[name] = True
        glBindTexture(textures[name].target, textures[name].id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 16, 16, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data[name])
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    glActiveTexture(GL_TEXTURE0 + textures[name].id)
    glBindTexture(textures[name].target, textures[name].id)

cube_signs = [
    (0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0),     # Left      (-X)
    (1, 0, 1), (1, 0, 0), (1, 1, 0), (1, 1, 1),     # Right     (+X)
    (0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1),     # Bottom    (-Y)
    (0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0),     # Top       (+Y)
    (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1),     # Front     (-Z)
    (1, 0, 0), (0, 0, 0), (0, 1, 0), (1, 1, 0)      # Back      (+Z)
]

cube_normals = [(-1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, -1.0), (0.0, 0.0, 1.0)]


def init():
    glEnable(GL_CULL_FACE)

    glClearDepth(1.0)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthFunc(GL_LEQUAL)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glShadeModel(GL_SMOOTH)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    global window, keys
    window = CameraWindow()
    keys = key.KeyStateHandler()
    window.push_handlers(keys)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    pyglet.app.run()


class VBO:
    def __init__(self):
        self.vertex_buffer_set = False
        self.color_buffer_set = False
        self.normal_buffer_set = False
        self.texture_buffer_set = False

        self.vertex_count = 0
        self.texture_id = None

        self.buffer_vertex = GLuint(0)
        self.buffer_color = GLuint(0)
        self.buffer_normal = GLuint(0)
        self.buffer_texture_coords = GLuint(0)

        glGenBuffers(1, self.buffer_vertex)
        glGenBuffers(1, self.buffer_color)
        glGenBuffers(1, self.buffer_normal)
        glGenBuffers(1, self.buffer_texture_coords)

    def data(self, buffer_type, data):
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

        elif buffer_type == "texture_coords":
            self.texture_buffer_set = True
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
            bind_texture(self.texture_id)
            self.texture()

        glDrawArrays(GL_QUADS, 0, self.vertex_count)


# noinspection PyCallingNonCallable
class Shader:
    def __init__(self, vert=None, frag=None, geom=None):
        self.handle = glCreateProgram()
        self.linked = False

        if vert is not None:
            self.create_shader(vert, GL_VERTEX_SHADER)

        if frag is not None:
            self.create_shader(frag, GL_FRAGMENT_SHADER)

        if geom is not None:
            self.create_shader(frag, GL_GEOMETRY_SHADER_EXT)

        self.link()

    def create_shader(self, strings, shader_type):
        count = len(strings)

        if count < 1:
            return

        byte_strings = [str.encode(s) for s in strings]

        shader = glCreateShader(shader_type)
        src = (c_char_p * count)(*byte_strings)
        glShaderSource(shader, count, cast(pointer(src), POINTER(POINTER(c_char))), None)

        glCompileShader(shader)
        temp = c_int(0)
        glGetShaderiv(shader, GL_COMPILE_STATUS, byref(temp))

        if not temp:
            glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(temp))
            buffer = create_string_buffer(temp.value)
            glGetShaderInfoLog(shader, temp, None, buffer)
            print(buffer.value)
        else:
            glAttachShader(self.handle, shader)

    def link(self):
        glLinkProgram(self.handle)
        temp = c_int(0)
        glGetProgramiv(self.handle, GL_LINK_STATUS, byref(temp))

        if not temp:
            glGetProgramiv(self.handle, GL_INFO_LOG_LENGTH, byref(temp))
            buffer = create_string_buffer(temp.value)
            glGetProgramInfoLog(self.handle, temp, None, buffer)
            print(buffer.value)
        else:
            self.linked = True

    def bind(self):
        glUseProgram(self.handle)

    @staticmethod
    def unbind():
        glUseProgram(0)

    def uniformf(self, name, *vals):
        if len(vals) in range(1, 5):
            {
                1: glUniform1f, 2: glUniform2f, 3: glUniform3f, 4: glUniform4f
            }[len(vals)](glGetUniformLocation(self.handle, str.encode(name)), *vals)

    def uniformi(self, name, *vals):
        if len(vals) in range(1, 5):
            {
                1: glUniform1i, 2: glUniform2i, 3: glUniform3i, 4: glUniform4i
            }[len(vals)](glGetUniformLocation(self.handle, str.encode(name)), *vals)

    def uniform_matrixf(self, name, mat):
        glUniformMatrix4fv(glGetUniformLocation(self.handle, str.encode(name)), 1, False, (GLfloat * len(mat))(*mat))


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
            pyglet.app.exit()

    def mouse_click(self, x, y, button, modifiers):
        hit = self.hitscan()

        if hit is not None:
            if button == 1:
                change_block_height(*hit, -1)

            elif button == 4:
                change_block_height(*hit, 1)

    def mouse_drag(self, x, y, dx, dy, buttons, modifers):
        self.mouse_move(x, y, dx, dy)

    def mouse_move(self, x, y, dx, dy):
        '''
        hit = self.hitscan()

        if hit is not None and hit != self.last_hit:
            if self.last_hit is not None:
                color_block(*self.last_hit, self.last_hit_color)
                self.last_hit = None
                self.last_hit_color = None
            else:
                self.last_hit = hit
                self.last_hit_color = get_block_color(*hit)
                color_block(*hit, (0.0, 1.0, 0.0, 1.0))
        '''

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
        self.current_chunk = (int(math.floor(self.world_pos[0] / chunk_size)), int(math.floor(self.world_pos[2] / chunk_size)))
        self.current_tile = (int(self.world_pos[0] - self.current_chunk[0] * chunk_size), int(self.world_pos[2] - self.current_chunk[1] * chunk_size))

    def hitscan(self):
        for offset in range(-1, -self.range, -1):
            checking_pos = numpy.dot([0, 0, offset, 1], numpy.linalg.inv(self.modelview))
            checking_chunk = (int(math.floor(checking_pos[0] / chunk_size)), int(math.floor(checking_pos[2] / chunk_size)))
            checking_tile = (int(checking_pos[0] - checking_chunk[0] * chunk_size), int(checking_pos[2] - checking_chunk[1] * chunk_size))

            if checking_chunk in active_chunks and checking_tile in chunk_height[checking_chunk]:
                if chunk_height[checking_chunk][checking_tile] >= round(checking_pos[1]):
                    return checking_chunk, checking_tile

    def update(self, dt):
        self.get_world_pos()

        try:
            self.key_loop(dt)
        except NameError:
            pass

        if not self.flying and self.current_chunk in active_chunks and self.current_tile in chunk_height[self.current_chunk]:
            height_diff = self.y - chunk_height[self.current_chunk][self.current_tile] - self.camera_height

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


# noinspection PyCallingNonCallable
def to_gl_float(data):
    return (GLfloat * len(data))(*data)


def get_block_color(chunk, tile):
    chunks[chunk].color()

    data = to_gl_float([0] * 4)
    glGetBufferSubData(GL_ARRAY_BUFFER, (tile[0] * chunk_size + tile[1]) * 384, 16, data)
    return list(data)


def color_block(chunk, tile, color):
    chunks[chunk].color()

    data = to_gl_float([*color] * 96)
    glBufferSubData(GL_ARRAY_BUFFER, (tile[0] * chunk_size + tile[1]) * 384, 384, data)


def change_block_height(chunk, tile, dh):
    tile_height = chunk_height[chunk][tile]
    cube_size = 72 * sizeof(c_float)

    chunks[chunk].vertex()

    tile_data = to_gl_float([0] * cube_size)
    glGetBufferSubData(GL_ARRAY_BUFFER, (tile[0] * chunk_size + tile[1]) * cube_size, cube_size, tile_data)

    new_data = to_gl_float([c + dh if c == tile_height else c for c in tile_data])
    glBufferSubData(GL_ARRAY_BUFFER, (tile[0] * chunk_size + tile[1]) * cube_size, cube_size, new_data)

    chunk_height[chunk][tile] += dh


def generate_chunk(cx, cz):
    chunk_height[(cx, cz)] = {}
    chunk_textures[(cx, cz)] = []
    data = {}

    for sx in range(chunk_size):
        for sz in range(chunk_size):
            x = sx + cx * chunk_size
            z = sz + cz * chunk_size
            noise_height = noise.snoise3(x / zoom, z / zoom, seed, octaves=3)

            cube_color = None
            data_id = None

            if -0.11 <= noise_height < 0.66:
                cube_color = (0.0, 0.5, 0.0, 1.0)

            if -1.0 <= noise_height < -0.33:
                data_id = "blue_wool"

            elif -0.33 <= noise_height < -0.11:
                data_id = "sand"

            elif -0.11 <= noise_height < 0.66:
                data_id = "grass"

            elif 0.66 <= noise_height <= 1.0:
                data_id = "snow"

            if data_id not in data:
                data[data_id] = {
                    "vertices": [],
                    "colors": [],
                    "normals": [],
                    "tex_coords": []
                }

            cube_height = round((noise_height + 1) * height_multiplier)
            chunk_height[(cx, cz)][(sx, sz)] = cube_height

            add_cube((x, 0, z), (1, cube_height, 1), cube_color, data[data_id]["vertices"], data[data_id]["colors"], data[data_id]["normals"], data[data_id]["tex_coords"])

    for data_id in data.keys():
        chunks[(cx, cz, data_id)] = VBO()
        chunks[(cx, cz, data_id)].texture_id = data_id
        chunks[(cx, cz, data_id)].data("vertex", data[data_id]["vertices"])
        chunks[(cx, cz, data_id)].data("normal", data[data_id]["normals"])
        chunks[(cx, cz, data_id)].data("texture_coords", data[data_id]["tex_coords"])

        if len(data[data_id]["colors"]) > 0:
            chunks[(cx, cz, data_id)].data("color", data[data_id]["colors"])

        chunk_textures[(cx, cz)].append(data_id)


def add_cube(pos, scale, color, verts, cols, norms, texts):
    tex_coords = [
        (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, -scale[1], 0.0), (0.0, -scale[1], 0.0),     # Left
        (scale[1], 0.0, 0.0), (scale[1], 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0),       # Right
        (1.0, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0),                 # Bottom
        (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0),                 # Top
        (0.0, 0.0, 1.0), (1.0, 0.0, 1.0), (1.0, scale[1], 1.0), (0.0, scale[1], 1.0),       # Front
        (1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, scale[1], 0.0), (1.0, scale[1], 0.0)        # Back
    ]

    w, h, d = scale

    vertices = []
    colors = []
    normals = []
    texture_coordinates = []

    for i, (sx, sy, sz) in enumerate(cube_signs):
        vertices.extend([pos[0] + (w * sx), pos[1] + (h * sy), pos[2] + (d * sz)])
        normals.extend([*cube_normals[i // 4]])
        texture_coordinates.extend([*tex_coords[i]])

        if color is not None:
            colors.extend([*color])

    if color is not None:
        cols.extend(colors)

    verts.extend(vertices)
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
            if (cx, cz) not in chunks:
                generate_chunk(cx, cz)
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

        # shader1.bind()

        for cx, cz in active_chunks:
            for texture in chunk_textures[(cx, cz)]:
                chunks[(cx, cz, texture)].draw()

        # shader1.unbind()

shader1 = Shader(['''

void main() {
    gl_TexCoord[0] = gl_MultiTexCoord0;
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}

'''], ['''

uniform sampler2D tex0;

void main() {
    gl_FragColor = texture2D(tex0, gl_TexCoord[0].st);
}

'''], None)

init()
