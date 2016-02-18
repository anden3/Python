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
    global terrain_vertices_vbo, terrain_colors_vbo, terrain_normals_vbo

    light_pos = (GLfloat * 4)(0, 100, 0, 0)
    mat_specular = (GLfloat * 4)(1, 1, 1, 1)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthFunc(GL_LEQUAL)

    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClearDepth(1.0)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glShadeModel(GL_SMOOTH)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    generate_terrain(100, 100, 10)

    terrain_vertices_vbo = VBO()
    terrain_vertices_vbo.data(terrain_vertices)

    terrain_colors_vbo = VBO()
    terrain_colors_vbo.data(terrain_colors)

    terrain_normals_vbo = VBO()
    terrain_normals_vbo.data(terrain_normals)


class VBO:
    def __init__(self):
        self.buffer = GLuint(0)
        glGenBuffers(1, self.buffer)

    def data(self, data):
        data_gl = (GLfloat * len(data))(*data)

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        glBufferData(GL_ARRAY_BUFFER, len(data) * 4, data_gl, GL_STATIC_DRAW)

    def bind(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)

    def vertex(self):
        self.bind()
        glVertexPointer(3, GL_FLOAT, 0, 0)

    def color(self):
        self.bind()
        glColorPointer(4, GL_FLOAT, 0, 0)

    def normal(self):
        self.bind()
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


def generate_terrain(width, depth, height_multiplier):
    for x in range(-(width // 2), width // 2):
        for z in range(-(depth // 2), width // 2):
            add_cube((x, noise.snoise2(x, z) * height_multiplier, z), (1.0, 1.0, 1.0), (0.0, 0.0, 1.0, 1.0), terrain_vertices, terrain_colors, terrain_normals)


def add_cube(pos, scale, color, verts, cols, norms):
    x, y, z = pos
    w, h, d = scale
    r, g, b, a = color

    vertices = []
    colors = []
    normals = []

    index = 0

    for sx, sy, sz in cube_signs:
        vertices.extend([x + (w * sx), y + (h * sy), z + (d * sz)])
        colors.extend([r, g, b, a])

        if index % 4 == 0:
            normals.extend([*cube_normals[index // 4]])

        index += 1

    verts.extend(vertices)
    cols.extend(colors)
    norms.extend(normals)


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

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        terrain_vertices_vbo.vertex()
        terrain_colors_vbo.color()
        terrain_normals_vbo.normal()

        glDrawArrays(GL_QUADS, 0, len(terrain_vertices) // 3)

        fps_display.draw()

init()
window = CameraWindow()
pyglet.app.run()
