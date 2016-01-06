from __future__ import division

from random import uniform

from pyglet import clock, font, window
from pyglet.gl import *

from math import cos, pi, sin, sqrt


class Position(object):

    @staticmethod
    def CoordsFromPolar(range, radians):
        x = range * sin(radians)
        y = range * cos(radians)
        return x, y

    @staticmethod
    def Random(xcentre, ycentre, maxrange):
        range = sqrt(uniform(0, maxrange ** 2))
        radians = uniform(0, 2*pi)
        x, y = Position.CoordsFromPolar(range, radians)
        return Position(x, y)

    def __init__(self, x, y, rot=None):
        self.x = x
        self.y = y
        if rot is None:
            self.rot = uniform(0, 2*pi)
        else:
            self.rot = rot


class Color(object):

    @staticmethod
    def Random(a=1.0):
        return Color(
            uniform(0, 1),
            uniform(0, 1),
            uniform(0, 1),
            a,
        )

    def __init__(self, r, g, b, a=1.0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    rgba = property(lambda self: (self.r, self.g, self.b, self.a))


class Entity(object):

    numShards = 7
    vertsGl = None

    @staticmethod
    def _generateVerts():
        verts = [0.0, 0.0]
        for i in range(0, Entity.numShards+ 1):
            bearing = i * 2 * pi / Entity.numShards
            radius = (2 + cos(bearing)) / 2
            x, y = Position.CoordsFromPolar(radius, bearing)
            verts.append(x)
            verts.append(y)
    
        Entity.vertsGl = (GLfloat * len(verts))(*verts)

    def __init__(self, id, size, x, y, rot):
        self.id = id
        self.pos = Position(x, y, rot)
        self.size = size
        self.dRot = 2 / self.size * uniform(-1, 1)
        self.__generateColors()

    def __generateColors(self):
        color = Color.Random()
        self.colors = [1, 1, 1, 1]
        for n in range(int(self.numShards / 2) + 2):
            self.colors.extend([color.r, color.g, color.b, 1])
            if n != int(self.numShards / 4):
                self.colors.extend([0, 0, 0, 0])
        self.colorsGl = (GLfloat * len(self.colors))(*self.colors)

    def tick(self):
        self.pos.rot += self.dRot

    def draw(self):
        glLoadIdentity()
        glTranslatef(self.pos.x, self.pos.y, 0)
        glRotatef(self.pos.rot, 0, 0, 1)
        glScalef(self.size, self.size, 1)
        glColorPointer(4, GL_FLOAT, 0, self.colorsGl)

        glDrawArrays(GL_TRIANGLE_FAN, 0, len(self.vertsGl) // 2)

Entity._generateVerts()


class World(object):

    numEnts = 85

    def __init__(self):
        self.ents = {}
        self.nextEntId = 0
        for id in range(self.numEnts):
            self.spawnEntity()

    def spawnEntity(self):
        size = uniform(0.4, 1.7) ** 2
        pos = Position.Random(0, 0, 8)
        pos.x *= 1.4
        ent = Entity(self.nextEntId, size, pos.x, pos.y, pos.rot)
        self.ents[ent.id] = ent
        self.nextEntId += 1
        return ent

    def tick(self):
        for ent in self.ents.values():
            ent.tick()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity();

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, Entity.vertsGl)

        for ent in self.ents.values():
            ent.draw()


class Camera(object):

    def __init__(self, win, world, x=0, y=0, rot=0, zoom=1):
        self.win = win
        self.world = world
        self.pos = Position(x, y, rot)
        self.zoom = zoom

    def worldProjection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        widthRatio = self.win.width / self.win.height
        gluOrtho2D(
            -self.zoom * widthRatio,
            self.zoom * widthRatio,
            -self.zoom,
            self.zoom)

    def hudProjection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.win.width, 0, self.win.height)


class Hud(object):

    def __init__(self, win, world):
        helv = font.load('Helvetica', 30)
        message = '%d fans, each %d triangles' % (
            world.numEnts, Entity.numShards)
        self.text = font.Text(
            helv,
            message,
            x=win.width,
            y=0,
            halign=font.Text.RIGHT,
            valign=font.Text.BOTTOM,
            color=(1, 1, 1, 0.5),
        )
        self.fps = clock.ClockDisplay(
            format="%(fps).1ffps",
            font=helv)

    def draw(self):
        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity();
        self.text.draw()
        self.fps.draw()


class App(object):

    def __init__(self):
        self.world = World()
        self.win = window.Window(fullscreen=True, vsync=True)
        self.camera = Camera(self.win, self.world, zoom=8)
        self.hud = Hud(self.win, self.world)
        # clock.set_fps_limit(30)
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        glClearColor(0, 0, 1, 1)

    def mainLoop(self):
        while not self.win.has_exit:
            self.win.dispatch_events()

            self.world.tick()

            self.camera.worldProjection()
            self.world.draw()

            self.camera.hudProjection()
            self.hud.draw()

            clock.tick()
            self.win.flip()

app = App()
app.mainLoop()

