import pyglet
from pyglet.gl import *
from pyglet.window import key

vertex_vbo = None
color_vbo = None

fps_display = pyglet.clock.ClockDisplay()

cube_signs = [
    (-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1),         # Top
    (-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1),     # Bottom
    (-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1),     # Left
    (1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1),         # Right
    (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),         # Front
    (1, -1, -1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1)      # Back
]

cube_vertices = []
cube_colors = []

cube_indexes = {}
cube_translations = {}


def init():
    global vertex_vbo, color_vbo

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthFunc(GL_LEQUAL)

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClearDepth(1.0)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glShadeModel(GL_SMOOTH)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    add_cube(1, (0.0, 0.0, 0.0), (1000.0, 1.0, 1000.0), (1.0, 1.0, 1.0, 1.0))
    add_cube(2, (0.0, 2.0, 0.0), (1.0, 1.0, 1.0), (1.0, 0.0, 0.0, 1.0))

    vertex_vbo = VBO()
    vertex_vbo.data(cube_vertices)

    color_vbo = VBO()
    color_vbo.data(cube_colors)


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

        elif symbol == key.LEFT:
            cube_translations[1][0] -= 5.0

        elif symbol == key.RIGHT:
            cube_translations[1][0] += 5.0

        elif symbol == key.UP:
            cube_translations[1][2] -= 5.0

        elif symbol == key.DOWN:
            cube_translations[1][2] += 5.0

        elif symbol == key.SPACE:
            cube_translations[1][1] += 5.0

        elif symbol == key.LSHIFT:
            cube_translations[1][1] -= 5.0

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


def add_cube(id, pos, scale, color):
    x, y, z = pos
    w, h, d = scale
    r, g, b, a = color

    vertices = []
    colors = []

    for sx, sy, sz in cube_signs:
        vertices.extend([x + (w * sx), y + (h * sy), z + (d * sz)])
        colors.extend([r, g, b, a])

    cube_indexes[id] = [(len(cube_vertices), len(cube_vertices) + len(vertices)),
                        (len(cube_colors), len(cube_colors) + len(colors))]
    cube_vertices.extend(vertices)
    cube_colors.extend(colors)

    cube_translations[id] = [0.0, 0.0, 0.0]


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
        fps_display.draw()

        glEnable(GL_DEPTH_TEST)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        vertex_vbo.vertex()
        color_vbo.color()

        for cube in cube_indexes:
            glTranslatef(*cube_translations[cube])
            glDrawArrays(GL_QUADS, cube_indexes[cube][0][0], cube_indexes[cube][0][1])
            glTranslatef(-cube_translations[cube][0], -cube_translations[cube][1], -cube_translations[cube][2])

init()
window = CameraWindow()
pyglet.app.run()
