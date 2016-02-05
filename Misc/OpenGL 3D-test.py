import pyglet
from pyglet.gl import *
from pyglet.window import key

fps_display = pyglet.clock.ClockDisplay()


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

        print("Viewport " + str(width) + "x" + str(height))

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
            print("Projection: 3D Perspective")
            self.mode = 1
            self.perspective()

        elif symbol == key.F2:
            print("Projection: 3D Isometric")
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


def init():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthFunc(GL_LEQUAL)

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClearDepth(1.0)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glShadeModel(GL_SMOOTH)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    pyglet.app.run()


def draw_cube(pos, scale, color):
    x, y, z = pos
    w, h, d = scale
    r, g, b, a = color

    glBegin(GL_QUADS)
    glColor4f(r, g, b, a)

    # Top
    glVertex3f(x - w, y + h, z - d)
    glVertex3f(x - w, y + h, z + d)
    glVertex3f(x + w, y + h, z + d)
    glVertex3f(x + w, y + h, z - d)

    # Bottom
    glVertex3f(x - w, y - h, z - d)
    glVertex3f(x + w, y - h, z - d)
    glVertex3f(x + w, y - h, z + d)
    glVertex3f(x - w, y - h, z + d)

    # Left
    glVertex3f(x - w, y - h, z - d)
    glVertex3f(x - w, y - h, z + d)
    glVertex3f(x - w, y + h, z + d)
    glVertex3f(x - w, y + h, z - d)

    # Right
    glVertex3f(x + w, y - h, z + d)
    glVertex3f(x + w, y - h, z - d)
    glVertex3f(x + w, y + h, z - d)
    glVertex3f(x + w, y + h, z + d)

    # Front
    glVertex3f(x - w, y - h, z + d)
    glVertex3f(x + w, y - h, z + d)
    glVertex3f(x + w, y + h, z + d)
    glVertex3f(x - w, y + h, z + d)

    # Back
    glVertex3f(x + w, y - h, z - d)
    glVertex3f(x - w, y - h, z - d)
    glVertex3f(x - w, y + h, z - d)
    glVertex3f(x + w, y + h, z - d)

    glEnd()


class CameraWindow(pyglet.window.Window):
    def __init__(self):
        super(CameraWindow, self).__init__(resizable=True)
        self.cam = Camera()
        self.on_resize = self.cam.view
        self.on_key_press = self.cam.key
        self.on_mouse_drag = self.cam.drag
        self.on_mouse_scroll = self.cam.scroll

    def on_draw(self):
        self.clear()
        self.cam.apply()
        fps_display.draw()

        for x in range(100):
            draw_cube((x, 1, 1), (1, 1, 1), (1.0, 0.0, 0.0, 1.0))
        # draw_cube((10, 1, 1), (2, 2, 2), (1.0, 0.0, 0.0, 0.1))

window = CameraWindow()
pyglet.app.run()
