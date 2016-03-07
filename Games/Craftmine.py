import math
import os
import random
import threading

import noise
import numpy
import pyglet
import pyglet.gl as gl
from pyglet.window import key

from OpenAL import *
from get_time import *

time = Time()

chunks = {}
active_chunks = set()
meshing_list = []

chunk_size = 16
chunk_height = 64
height_offset = 64
render_distance = 7

window_width, window_height = 0, 0

zoom = 100

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

    init_gl()
    init_textures()
    init_sounds()
    init_terrain()

    global window, keys
    window = CameraWindow()
    keys = key.KeyStateHandler()
    window.push_handlers(keys)

    pyglet.app.run()


def init_gl():
    gl.glClearDepth(1.0)

    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glDepthFunc(gl.GL_LEQUAL)

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LEQUAL)
    gl.glShadeModel(gl.GL_SMOOTH)
    gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST)

    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)


def init_textures():
    global texture_pos, texture, texture_data

    images = [pyglet.image.load('images/' + file).get_image_data() for file in os.listdir('images')
              if file.endswith('.png')]

    area = len(images) * 256
    area_root = math.sqrt(area)

    if area_root % 32 != 0:
        atlas_width = int(area_root - (area_root % 32))
        atlas_height = int(area / atlas_width)

        if atlas_height % 32 != 0:
            atlas_height += int(32 - (atlas_height % 32))
    else:
        atlas_width, atlas_height = int(area_root), int(area_root)

    texture_atlas = pyglet.image.atlas.TextureAtlas(width=atlas_width, height=atlas_height)

    texture_pos = {}

    for i, image in enumerate(images):
        texture_region = texture_atlas.add(image)
        texture_pos[i + 1] = [
            [texture_region.x / atlas_width, texture_region.y / atlas_height],
            [(texture_region.x + 16) / atlas_width, (texture_region.y + 16) / atlas_height]
        ]

    texture = texture_atlas.texture
    texture_data = texture.get_image_data().get_data("RGB", texture.width * 3)


def init_sounds():
    global sounds, listener
    sounds = {}

    for file in os.listdir("sounds"):
        if file.endswith(".wav"):
            if int(file[:1]) not in sounds:
                sounds[int(file[:1])] = ["sounds/" + file]
            else:
                sounds[int(file[:1])].append("sounds/" + file)

    listener = Listener()


def init_terrain():
    global chunk_density
    chunk_density = numpy.zeros((chunk_size, height_offset, chunk_size), dtype=numpy.float32)

    for sx in range(chunk_size):
        for sy in range(height_offset):
            for sz in range(chunk_size):
                chunk_density.itemset((sx, sy, sz), noise.snoise3(sx / 10, sy / 10, sz / 10))

    chunks[(0, 0)] = Chunk((0, 0))
    chunks[(0, 0)].generate()
    chunks[(0, 0)].mesh()


class VBO:
    def __init__(self, size=None):
        if size is None:
            self.buffer_size = chunk_size ** 2 * chunk_height * 24 * 2
        else:
            self.buffer_size = size

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
            self.buffers[buffer] = gl.GLuint(0)
            gl.glGenBuffers(1, self.buffers[buffer])
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[buffer])
            gl.glBufferData(gl.GL_ARRAY_BUFFER, self.buffer_size, None, gl.GL_DYNAMIC_DRAW)

    def data(self, buffer_type, data, offset):
        if buffer_type != "texture":
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers[buffer_type])

            if buffer_type == "color":
                offset *= 16
            else:
                offset *= 12

            gl_data = to_gl_float(data)
            length = len(data) * 4
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, offset, length, gl_data)

            if buffer_type == "vertex":
                self.vertex_count += int(len(data) / 3)

        else:
            self.buffers[buffer_type] = gl.GLuint(0)
            gl.glGenTextures(1, self.buffers[buffer_type])
            gl.glBindTexture(data.target, data.id)

            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, texture.width, texture.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE,
                            texture_data)

    def vertex(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers["vertex"])
        gl.glVertexPointer(3, gl.GL_FLOAT, 0, 0)

    def color(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers["color"])
        gl.glColorPointer(4, gl.GL_FLOAT, 0, 0)

    def normal(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers["normal"])
        gl.glNormalPointer(gl.GL_FLOAT, 0, 0)

    def texture(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffers["texture_coords"])
        gl.glTexCoordPointer(3, gl.GL_FLOAT, 0, 0)

    def draw(self):
        if self.buffers["vertex"] is not None:
            gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
            self.vertex()

        if self.buffers["color"] is not None:
            gl.glEnableClientState(gl.GL_COLOR_ARRAY)
            self.color()

        if self.buffers["normal"] is not None:
            gl.glEnableClientState(gl.GL_NORMAL_ARRAY)
            self.normal()

        if self.buffers["texture_coords"] is not None:
            gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
            gl.glEnable(gl.GL_TEXTURE_2D)
            gl.glBindTexture(texture.target, texture.id)
            self.texture()

        gl.glDrawArrays(gl.GL_QUADS, 0, self.vertex_count)


# noinspection PyUnusedLocal
class Camera(object):
    x, y, z = 0, chunk_height + height_offset - 5, 0
    rx, ry = 340, 0
    w, h = window_width, window_height
    far = 8192
    fov = 90

    width, depth = 0.2, 0.2

    vx, vy, vz = 0, 0, 0
    velocity = (0, 0, 0)

    speed_mult = 5
    jump_height = 4
    camera_height = 1.7
    range = 5

    world_pos = None
    current_chunk = (0, 0)
    current_tile = (0, y, 0)

    inv_modelview = None
    forward_vector = (0, 0, 1)
    up_vector = (0, 1, 0)

    flying = False
    jumping = False

    holding_block = 1

    ui = VBO(size=1000)

    def view(self, width, height):
        self.w, self.h = width, height
        gl.glViewport(0, 0, width, height)
        self.perspective()

    def perspective(self):
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluPerspective(self.fov, self.w / self.h, 0.1, self.far)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def ui_mode(self):
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glDisable(gl.GL_LIGHTING)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluOrtho2D(-self.w / 2, self.w / 2, -self.h / 2, self.h / 2)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

    def init_ui(self):
        self.ui.data("texture", texture, 0)

        vertices, colors, tex_coords = [], [], []

        add_rect(window_width / 2 - 16, window_height / 2 - 1, 32, 2, (1.0, 1.0, 1.0, 1.0), vertices, colors, tex_coords)
        add_rect(window_width / 2 - 1, window_height / 2 - 16, 2, 32, (1.0, 1.0, 1.0, 1.0), vertices, colors, tex_coords)
        add_rect(window_width / 2 - 16, 200, 32, 32, (1.0, 1.0, 1.0, 1.0), vertices, colors, tex_coords, image=self.holding_block)

        self.ui.data("vertex", to_gl_float(vertices), 0)
        self.ui.data("color", to_gl_float(colors), 0)
        self.ui.data("texture_coords", to_gl_float(tex_coords), 0)

    def update_ui(self):
        vertices, colors, tex_coords = [], [], []

        add_rect(window_width / 2 - 16, 200, 32, 32, (1.0, 1.0, 1.0, 1.0), vertices, colors, tex_coords, image=self.holding_block)

        self.ui.data("vertex", to_gl_float(vertices), 8)
        self.ui.data("color", to_gl_float(colors), 8)
        self.ui.data("texture_coords", to_gl_float(tex_coords), 8)

    def key_loop(self, dt):
        if keys[key.LSHIFT]:
            self.speed_mult = 25
        else:
            self.speed_mult = 5

        if keys[key.MINUS]:  # Actually Plus...
            self.fov -= self.speed_mult * dt
            self.perspective()

        elif keys[key.SLASH]:  # Actually Minus...
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

    # noinspection PyProtectedMember
    def key_down(self, symbol, modifiers):
        if symbol == key.F:
            self.flying = not self.flying

        elif symbol == key._1:
            self.holding_block = 1
            self.update_ui()

        elif symbol == key._2:
            self.holding_block = 2
            self.update_ui()

        elif symbol == key._3:
            self.holding_block = 3
            self.update_ui()

        elif symbol == key._4:
            self.holding_block = 4
            self.update_ui()

        elif symbol == key.ESCAPE:
            time.get(get_type="all")

            get_function_avg()

            pyglet.app.exit()

    def mouse_click(self, x, y, button, modifiers):
        hit = self.hitscan()

        if hit is not None and hit[0] is not None and hit[1] is not None:
            if button == 1:
                chunks[hit[0]].remove_block(hit[1])
            elif button == 4 and len(hit) == 3:
                if sounds.get(self.holding_block) is not None:
                    play_sound(random.choice(sounds[self.holding_block]), get_world_pos(hit[2][0], hit[2][1]))

                chunks[hit[2][0]].create_block(hit[2][1], new=self.holding_block)

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
        gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX, modelview)

        modelview_list = [[modelview[w + h * 4] for w in range(4)] for h in range(4)]
        self.inv_modelview = numpy.linalg.inv(modelview_list)

        self.up_vector = list(self.inv_modelview[1][:3])
        self.forward_vector = list(self.inv_modelview[2][:3])
        self.world_pos = self.inv_modelview[3][:3]

        self.current_chunk, self.current_tile = get_chunk_pos(self.world_pos)

    def hitscan(self):
        last_pos = None

        for offset in numpy.arange(0, -self.range, -0.1):
            checking_pos = numpy.dot([0, 0, offset, 1], self.inv_modelview)
            checking_chunk, checking_tile = get_chunk_pos(checking_pos)

            sx, sy, sz = checking_tile

            if checking_chunk in active_chunks:
                if checking_tile in chunks[checking_chunk].blocks:
                    if last_pos is not None and get_chunk_pos(last_pos) is not None:
                        return checking_chunk, checking_tile, get_chunk_pos(last_pos)
                    else:
                        return checking_chunk, checking_tile

            last_pos = checking_pos

    def get_bounding_box(self, dt):
        x = self.x + self.vx
        y = self.y
        z = self.z + self.vz

        points = [
            (x - self.width / 2, y - 1, z), (x + self.width / 2, y - 1, z),
            (x - self.width / 2, y, z), (x + self.width / 2, y, z),
            (x, y - 1, z - self.depth / 2), (x, y - 1, z + self.depth / 2),
            (x, y, z - self.depth / 2), (x, y, z + self.depth / 2),
            (x, y - 1.7, z), (x, y + 0.7, z)
        ]

        for i, corner in enumerate(points):
            chunk, pos = get_chunk_pos(corner)

            if chunks[chunk].block_map.item(pos) > 0:
                if (i == 0 or i == 2) and self.vx < 0:      # Left
                    self.vx = 0

                elif (i == 1 or i == 3) and self.vx > 0:    # Right
                    self.vx = 0

                elif (i == 4 or i == 6) and self.vz < 0:    # Back
                    self.vz = 0

                elif (i == 5 or i == 7) and self.vz > 0:    # Front
                    self.vz = 0

                elif i == 8:                                # Down
                    if self.vy < 0:
                        self.vy = 0

                    if keys[key.SPACE]:
                        self.vy += self.jump_height

                    if self.vy > self.jump_height:
                        self.vy = self.jump_height

                elif i == 9 and self.vy > 0:                # Up
                    self.vy = 0
            else:
                if i == 8:
                    self.vy -= 9.82 * dt

    def update(self, dt):
        self.get_world_pos()

        if dt >= 0.1:
            return

        try:
            self.key_loop(dt)
        except NameError:
            pass

        if not self.flying and self.current_chunk in active_chunks:
            if 2 <= self.y < chunk_height + height_offset - 1:
                self.get_bounding_box(dt)
            else:
                self.vy -= 9.82 * dt
        else:
            self.vy = 0

        self.velocity = (self.vx, self.vy, self.vz)

        self.x += self.vx
        self.y += self.vy * dt
        self.z += self.vz

        listener.position = (self.x, self.y, self.z)
        listener.orientation = self.forward_vector + self.up_vector

        self.vx = 0
        self.vz = 0

    def apply(self):
        gl.glLoadIdentity()
        gl.glRotatef(-self.rx, 1, 0, 0)
        gl.glRotatef(-self.ry, 0, 1, 0)
        gl.glTranslatef(-self.x, -self.y, -self.z)


class Chunk:
    def __init__(self, pos):
        self.cx, self.cz = pos

        self.vbo = VBO()
        self.blocks = set()

        self.offset = 0

        self.block_map = numpy.zeros((chunk_size, chunk_height + height_offset, chunk_size), dtype=numpy.uint8)
        self.offsets = numpy.zeros((chunk_size, chunk_height + height_offset, chunk_size), dtype=numpy.uint32)

        self.is_meshed = False
        self.generated_ores = False

    def generate(self):
        for sx in range(chunk_size):
            x = sx + self.cx * chunk_size

            for sz in range(chunk_size):
                z = sz + self.cz * chunk_size

                height = round((noise.snoise3(x / zoom, z / zoom, seed, octaves=3) + 1) / 2 * chunk_height) + height_offset
                block_id = None

                if 114 <= height:
                    block_id = 1

                elif 90 <= height < 114:
                    block_id = 2

                elif 82 <= height < 90:
                    block_id = 3

                elif height < 82:
                    block_id = 4

                for y in range(height - 1, height + 1):
                    self.blocks.add((sx, y, sz))

                if block_id == 2:
                    self.block_map[sx, height, sz] = 2
                    self.block_map[sx, height - 4:height, sz] = 8
                else:
                    self.block_map[sx, height - 4:height + 1, sz] = block_id

                self.block_map[sx, 1:height - 4, sz] = 5
                self.block_map[sx, 0, sz] = 7

    def generate_ores(self):
        deposit_locations = [random_chunk_pos() for _ in range(20)]

        for pos in deposit_locations:
            new_pos = pos
            added_blocks = {new_pos}

            for _ in range(6):
                min_density = 1
                min_density_block = None

                for chunk, neighbor in get_neighbors(new_pos):
                    if chunk == (self.cx, self.cz):
                        if neighbor not in added_blocks and 0 <= neighbor[1] < chunk_height:
                            block_density = chunk_density.item(neighbor)

                            if block_density < min_density:
                                min_density = block_density
                                min_density_block = neighbor

                if min_density_block is not None:
                    added_blocks.add(min_density_block)
                    self.block_map.itemset(min_density_block, 6)
                    new_pos = min_density_block

    def mesh(self):
        if not self.is_meshed:
            for gx in [-1, 0, 1]:
                for gz in [-1, 0, 1]:
                    chunk_pos = (self.cx + gx, self.cz + gz)

                    if chunk_pos != (self.cx, self.cz) and chunk_pos not in chunks:
                        chunks[chunk_pos] = Chunk(chunk_pos)
                        chunks[chunk_pos].generate()

        if not self.generated_ores:
            self.generated_ores = True
            self.generate_ores()

        self.vbo.data("texture", texture, 0)

        data = ([], [], [])
        data_names = ["vertex", "normal", "texture_coords"]

        for pos in self.blocks.copy():
            self.add_block(pos, data)

        for i, data_list in enumerate(data):
            self.vbo.data(data_names[i], data_list, 0)

        self.is_meshed = True

    def remove_block(self, tile):
        if sounds.get(self.block_map.item(tile)) is not None:
            play_sound(random.choice(sounds[self.block_map.item(tile)]), get_world_pos((self.cx, self.cz), tile))

        self.blocks.remove(tile)
        self.block_map.itemset(tile, 0)
        self.offsets.itemset(tile, 0)

        self.vbo = VBO()
        self.offset = 0

        chunk_list = []

        for chunk, neighbor in get_neighbors(get_world_pos((self.cx, self.cz), tile)):
            if chunk != (self.cx, self.cz):
                chunk_list.append(chunk)

            if neighbor not in chunks[chunk].blocks:
                chunks[chunk].blocks.add(neighbor)

        self.mesh()

        if len(chunk_list) > 0:
            for chunk in chunk_list:
                chunks[chunk].vbo = VBO()
                chunks[chunk].offset = 0
                chunks[chunk].mesh()

    def create_block(self, tile, new=None):
        data_names = ["vertex", "normal", "texture_coords"]

        if new:
            self.blocks.add(tile)
            self.block_map.itemset(tile, new)

        data = ([], [], [])

        if self.add_block(tile, data):
            offset = self.offsets.item(tile)

            for i, data_list in enumerate(data):
                self.vbo.data(data_names[i], data_list, offset)

    def add_block(self, tile, data):
        x, y, z = get_world_pos((self.cx, self.cz), tile)
        neighbors = get_neighbors((x, y, z), get_faces=True)

        if sum(neighbors) == 6:
            self.blocks.remove(tile)
            return False

        for i, face in enumerate(neighbors):
            if face == 0:
                add_face((x, y, z), i, self.block_map.item(tile), *data)

        self.offsets.itemset(tile, self.offset)
        self.offset += (6 - sum(neighbors)) * 4
        return True


def get_neighbors(pos, get_faces=False):
    x, y, z = pos

    neighbors = [
        (x - 1, y, z), (x + 1, y, z),
        (x, y - 1, z), (x, y + 1, z),
        (x, y, z + 1), (x, y, z - 1)
    ]

    tile_neighbors = []

    for neighbor in neighbors:
        chunk, tile = get_chunk_pos(neighbor)

        if get_faces:
            tile_neighbors.append(1 if chunks[chunk].block_map.item(tile) > 0 else 0)
        else:
            if chunks[chunk].block_map.item(tile) > 0:
                tile_neighbors.append((chunk, tile))

    return tile_neighbors


# noinspection PyCallingNonCallable
def to_gl_float(data):
    return (gl.GLfloat * len(data))(*data)


def get_chunk_pos(pos):
    chunk = (int(math.floor(pos[0] / chunk_size)), int(math.floor(pos[2] / chunk_size)))
    tile = (int(pos[0] - chunk[0] * chunk_size), int(pos[1]), int(pos[2] - chunk[1] * chunk_size))

    return chunk, tile


def get_world_pos(chunk, tile):
    return chunk[0] * chunk_size + tile[0], tile[1], chunk[1] * chunk_size + tile[2]


def clamp(values):
    return tuple([(x - min(values)) / (max(values) - min(values)) for x in values])


def normalize(vector):
    vector_length = math.sqrt(sum([v ** 2 for v in vector]))
    return tuple([v / vector_length for v in vector])


def random_chunk_pos(height=False):
    return random.randrange(chunk_size), random.randrange(height if height else height_offset), random.randrange(chunk_size)


def play_sound(file, pos):
    sound = LoadSound(file)
    player = SoundPlayer()

    player.position = pos
    player.loop = False
    player.volume = 0.5
    player.rolloff = 1

    player.add(sound)
    player.play()

    threading.Timer(sound.duration, clean_up_sound, [sound, player]).start()


def clean_up_sound(sound, player):
    player.stop()
    player.delete()
    sound.delete()


def add_face(pos, face, texture_name, verts, norms, texts, scale=(1.0, 1.0, 1.0)):
    x, y, z = pos
    w, h, d = scale
    texture_positions = texture_pos[texture_name]

    vertices = []
    normals = []
    tex_coords = []

    for tx, ty, tz in [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]:
        tex_coords.append(texture_positions[tx][0] * w)
        tex_coords.append(texture_positions[ty][1] * h)
        tex_coords.append(0)

    for i, (sx, sy, sz) in enumerate(cube_signs[face]):
        vertices.extend([x + (w * sx), y + (h * sy), z + (d * sz)])
        normals.extend([*cube_normals[face]])

    verts.extend(vertices)
    norms.extend(normals)
    texts.extend(tex_coords)


def add_rect(x, y, w, h, color, verts, cols, texts, image=None):
    x -= window_width / 2
    y -= window_height / 2

    verts.extend([x + w, y + h, 0, x + w, y, 0, x, y, 0, x, y + h, 0])
    cols.extend([*color] * 4)

    if image:
        texture_positions = texture_pos[image]

        texts.extend([
            texture_positions[0][0], texture_positions[0][1], 0,
            texture_positions[1][0], texture_positions[0][1], 0,
            texture_positions[1][0], texture_positions[1][1], 0,
            texture_positions[0][0], texture_positions[1][1], 0,
        ])
    else:
        texts.extend([0] * 12)


def render_light(pos, attenuation=0):
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, to_gl_float((0.2, 0.2, 0.2, 1.0)))
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, to_gl_float((1.0, 1.0, 1.0, 1.0)))
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, to_gl_float((0.5, 0.5, 0.5, 1.0)))

    gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, to_gl_float((*pos, attenuation)))

    gl.glEnable(gl.GL_LIGHT0)


def check_draw_distance(chunk):
    active_chunks.clear()

    new_chunks = []

    for cx in range(chunk[0] - render_distance, chunk[0] + render_distance + 1):
        for cz in range(chunk[1] - render_distance, chunk[1] + render_distance + 1):
            pos = (cx, cz)
            dist = (chunk[0] - cx) ** 2 + (chunk[1] - cz) ** 2

            if dist <= render_distance ** 2:
                if pos not in meshing_list:
                    if pos not in chunks:
                        chunks[pos] = Chunk(pos)
                        chunks[pos].generate()
                        new_chunks.append((pos, dist))

                    elif not chunks[pos].is_meshed:
                        new_chunks.append((pos, dist))

                active_chunks.add(pos)

    if len(new_chunks) > 0:
        meshing_list.extend([c for c, d in sorted(new_chunks, key=lambda x: x[1])])


class CameraWindow(pyglet.window.Window):
    def __init__(self):
        super(CameraWindow, self).__init__(resizable=True, vsync=False)
        self.maximize()
        self.set_fullscreen()

        global window_width, window_height
        window_width, window_height = self.width, self.height

        self.set_exclusive_mouse(True)

        self.cam = Camera()
        self.on_resize = self.cam.view
        self.on_key_press = self.cam.key_down
        self.on_mouse_press = self.cam.mouse_click
        self.on_mouse_drag = self.cam.mouse_drag
        self.on_mouse_motion = self.cam.mouse_move

        self.cam.update(0.0)
        self.cam.init_ui()

        pyglet.clock.schedule_interval(self.cam.update, 1 / 60)

    def on_draw(self):
        gl.glClearColor(0.5, 0.69, 1.0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        self.cam.apply()

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_CULL_FACE)

        render_light((2, 10, -2))

        gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE, to_gl_float([0.7, 0.7, 0.7, 1.0]))

        check_draw_distance(self.cam.current_chunk)

        if len(meshing_list) > 0:
            chunks[meshing_list.pop(0)].mesh()

        for chunk in active_chunks:
            chunks[chunk].vbo.draw()

        self.cam.ui_mode()

        self.cam.ui.draw()

        self.cam.perspective()
        self.cam.apply()

init()
