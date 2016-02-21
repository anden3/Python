import math
import random
from ctypes import *

import noise
import numpy
import pyglet
from pyglet.gl import *
from pyglet.window import key

chunks = {}
chunk_height = {}
active_chunks = set()

chunk_size = 16
height_multiplier = 30
zoom = 100
render_distance = 3

seed = random.uniform(-1000, 1000)

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

    pyglet.app.run()


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
        if buffer_type == "vertex":
            self.vertex_buffer_set = True
            glBindBuffer(GL_ARRAY_BUFFER, self.buffer_vertex)

        elif buffer_type == "color":
            self.color_buffer_set = True
            glBindBuffer(GL_ARRAY_BUFFER, self.buffer_color)

        elif buffer_type == "normal":
            self.normal_buffer_set = True
            glBindBuffer(GL_ARRAY_BUFFER, self.buffer_normal)

        glBufferData(GL_ARRAY_BUFFER, len(data) * 4, to_gl_float(data), GL_STATIC_DRAW)

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
    range = 10

    world_pos = None
    current_chunk = None
    current_tile = None
    modelview = None

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
            pyglet.app.exit()

    def mouse_click(self, x, y, button, modifiers):
        hit = self.hitscan()

        if hit is not None:
            if button == 1:
                change_block_height(*hit, -1)

            elif button == 4:
                change_block_height(*hit, 1)

    def mouse_drag(self, x, y, dx, dy, buttons, modifers):
        hit = self.hitscan()

        if hit is not None:
            if buttons == 1:
                change_block_height(*hit, -1)

            elif buttons == 4:
                change_block_height(*hit, 1)

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
        self.current_chunk = (int(math.floor(self.world_pos[0] / chunk_size)), int(math.floor(self.world_pos[2] / chunk_size)))
        self.current_tile = (int(self.world_pos[0] - self.current_chunk[0] * chunk_size), int(self.world_pos[2] - self.current_chunk[1] * chunk_size))

    def hitscan(self):
        for offset in range(-1, -self.range, -1):
            checking_pos = numpy.dot([0, 0, offset, 1], numpy.linalg.inv(self.modelview))
            checking_height = round(checking_pos[1])
            checking_chunk = (int(math.floor(checking_pos[0] / chunk_size)), int(math.floor(checking_pos[2] / chunk_size)))
            checking_tile = (int(checking_pos[0] - checking_chunk[0] * chunk_size), int(checking_pos[2] - checking_chunk[1] * chunk_size))

            if checking_chunk in active_chunks and checking_tile in chunk_height[checking_chunk]:
                if chunk_height[checking_chunk][checking_tile] == checking_height:
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


def color_block(chunk, tile, color):
    chunks[chunk].color()
    cube_size = 96 * sizeof(c_float)
    data = to_gl_float([*color] * int(cube_size / 4))
    glBufferSubData(GL_ARRAY_BUFFER, (tile[0] * chunk_size + tile[1]) * cube_size, cube_size, data)


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
    c_vertices = []
    c_colors = []
    c_normals = []

    chunk_height[(cx, cz)] = {}

    for sx in range(chunk_size):
        for sz in range(chunk_size):
            x = sx + cx * chunk_size
            z = sz + cz * chunk_size
            noise_height = noise.snoise3(x / zoom, z / zoom, seed, octaves=3)
            cube_color = None

            if -1.0 <= noise_height < -0.33:
                cube_color = (0.0, 0.0, 0.5, 1.0)
            elif -0.33 <= noise_height < -0.11:
                cube_color = (0.76, 0.70, 0.50, 1.0)
            elif -0.11 <= noise_height < 0.66:
                cube_color = (0.0, 0.5, 0.0, 1.0)
            elif 0.66 <= noise_height <= 1.0:
                cube_color = (0.8, 0.8, 0.8, 1.0)

            cube_height = round((noise_height + 1) * height_multiplier)
            chunk_height[(cx, cz)][(sx, sz)] = cube_height

            add_cube((x, 0, z), (1, cube_height, 1), cube_color, c_vertices, c_colors, c_normals)

    chunks[(cx, cz)] = VBO()
    chunks[(cx, cz)].data(c_vertices, "vertex")
    chunks[(cx, cz)].data(c_colors, "color")
    chunks[(cx, cz)].data(c_normals, "normal")

    chunk_buffer_length[(cx, cz)] = chunk_size ** 2 * 24


def add_cube(pos, scale, color, verts, cols, norms):
    w, h, d = scale

    vertices = []
    colors = []
    normals = []

    for i, (sx, sy, sz) in enumerate(cube_signs):
        vertices.extend([pos[0] + (w * sx), pos[1] + (h * sy), pos[2] + (d * sz)])
        colors.extend([*color])
        normals.extend([*cube_normals[i // 4]])

    verts.extend(vertices)
    cols.extend(colors)
    norms.extend(normals)


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

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        check_draw_distance()

        # shader1.bind()

        for chunk in active_chunks:
            chunks[chunk].draw()

        # shader1.unbind()

shader1 = Shader(['''
    varying vec3 N;
    varying vec3 v;

    void main() {
        v = vec3(gl_ModelViewMatrix * gl_Vertex);
        N = normalize(gl_NormalMatrix * gl_Normal);

        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    }
'''], ['''
    varying vec3 N;
    varying vec3 v;

    void main() {
        vec3 L = normalize(gl_LightSource[0].position.xyz - v);
        vec3 E = normalize(-v);
        vec3 R = normalize(-reflect(L, N));

        vec4 Iamb = gl_FrontLightProduct[0].ambient;

        vec4 Idiff = gl_FrontLightProduct[0].diffuse * max(dot(N, L), 0.0);
        Idiff = clamp(Idiff, 0.0, 1.0);

        vec4 Ispec = gl_FrontLightProduct[0].specular * pow(max(dot(R, E), 0.0), 0.3 * gl_FrontMaterial.shininess);
        Idiff = clamp(Idiff, 0.0, 1.0);

        gl_FragColor = gl_FrontLightModelProduct.sceneColor + Iamb + Idiff + Ispec;
    }
'''], None)

init()
