import noise
import pyglet
from pyglet.gl import *
from pyglet.window import key

fps_display = pyglet.clock.ClockDisplay()

cube_signs = [
    (-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1),         # Top
    (-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1),     # Bottom
    (-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1),     # Left
    (1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1),         # Right
    (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),         # Front
    (1, -1, -1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1)      # Back
]

terrain_vertices = []
terrain_colors = []
terrain_normals = []

cube_normals = [
    (0.0, 1.0, 0.0),      # Top
    (0.0, -1.0, 0.0),     # Bottom
    (-1.0, 0.0, 0.0),     # Left
    (1.0, 0.0, 0.0),      # Right
    (0.0, 0.0, -1.0),     # Front
    (0.0, 0.0, 1.0)       # Back
]


def init():
    global terrain

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClearDepth(1.0)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthFunc(GL_LEQUAL)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glShadeModel(GL_SMOOTH)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    generate_terrain(200, 200, 3)

    terrain = VBO()
    terrain.data(terrain_vertices, "vertex")
    terrain.data(terrain_colors, "color")
    terrain.data(terrain_normals, "normal")


class VBO:
    def __init__(self):
        self.buffer_vertex = GLuint(0)
        self.buffer_color = GLuint(0)
        self.buffer_normal = GLuint(0)

        glGenBuffers(1, self.buffer_vertex)
        glGenBuffers(1, self.buffer_color)
        glGenBuffers(1, self.buffer_normal)

    def data(self, data, buffer_type):
        data_gl = to_gl_float(data)

        if buffer_type == "vertex":
            glBindBuffer(GL_ARRAY_BUFFER, self.buffer_vertex)
        elif buffer_type == "color":
            glBindBuffer(GL_ARRAY_BUFFER, self.buffer_color)
        elif buffer_type == "normal":
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


class Camera(object):
    mode = 1
    x, y, z = 0, 0, 512
    rx, ry, rz = 30, -45, 0
    w, h = 640, 480
    far = 8192
    fov = 90

    def view(self, width, height):
        self.w, self.h = width, height
        glViewport(0, 0, width, height)

        if self.mode == 1:
            self.perspective()
        elif self.mode == 2:
            self.isometric()

    def isometric(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-self.w / 2.0, self.w / 2.0, -self.h / 2.0, self.h / 2.0, 0, self.far)
        glMatrixMode(GL_MODELVIEW)

    def perspective(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, float(self.w) / self.h, 0.1, self.far)
        glMatrixMode(GL_MODELVIEW)

    def key(self, symbol, modifiers):
        if symbol == key.F1:
            self.mode = 1
            self.perspective()

        elif symbol == key.F2:
            self.mode = 2
            self.isometric()

        elif self.mode == 1 and symbol == key.NUM_SUBTRACT:
            self.fov -= 1
            self.perspective()

        elif self.mode == 1 and symbol == key.NUM_ADD:
            self.fov += 1
            self.perspective()

    def drag(self, x, y, dx, dy, button, modifiers):
        if button == 1:
            self.x -= dx * 2
            self.y -= dy * 2

        elif button == 4:
            self.ry += dx / 4
            self.rx -= dy / 4

    def scroll(self, x, y, scroll_x, scroll_y):
        self.z -= scroll_y * 10

    def apply(self):
        glLoadIdentity()
        glTranslatef(-self.x, -self.y, -self.z)
        glRotatef(self.rx, 1, 0, 0)
        glRotatef(self.ry, 0, 1, 0)
        glRotatef(self.rz, 0, 0, 1)


def to_gl_float(data):
    return (GLfloat * len(data))(*data)


def generate_terrain(width, depth, height_multiplier):
    for x in range(-(width // 2), width // 2):
        for z in range(-(depth // 2), width // 2):
            cube_height = noise.snoise2(x / 20, z / 20)
            cube_color = None

            if -1.0 <= cube_height < -0.33:
                cube_color = (0.0, 0.0, 1.0, 1.0)
            elif -0.33 <= cube_height < 0.33:
                cube_color = (0.0, 1.0, 0.0, 1.0)
            elif 0.33 <= cube_height <= 1.0:
                cube_color = (1.0, 0.0, 0.0, 1.0)

            add_cube((x, round(cube_height * height_multiplier), z), (1.0, 1.0, 1.0), cube_color, terrain_vertices, terrain_colors, terrain_normals)


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


class CameraWindow(pyglet.window.Window):
    def __init__(self):
        super(CameraWindow, self).__init__(resizable=True)
        self.maximize()

        self.cam = Camera()
        self.on_resize = self.cam.view
        self.on_key_press = self.cam.key
        self.on_mouse_drag = self.cam.drag
        self.on_mouse_scroll = self.cam.scroll

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

        terrain.vertex()
        terrain.color()
        terrain.normal()

        glDrawArrays(GL_QUADS, 0, len(terrain_vertices) // 3)

        fps_display.draw()

init()
window = CameraWindow()
pyglet.app.run()
