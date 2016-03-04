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
chunk_height = 64
height_offset = 64
render_distance = 3

window_width, window_height = 0, 0

zoom = 100

seed = random.uniform(-1000, 1000)

directions = ["left", "right", "bottom", "top", "front", "back"]

texture_pos = {
    1: (0, 0),
    2: (1, 0),
    3: (0, 1),
    4: (1, 1)
}

texture_color = {
    1: (0.8, 0.8, 0.8, 1.0),
    2: (0.0, 0.5, 0.0, 1.0),
    3: (0.76, 0.7, 0.5, 1.0),
    4: (0.0, 0.0, 0.5, 1.0)
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

    images = [
        pyglet.image.load("images/snow.png").get_image_data(),
        pyglet.image.load("images/grass_top.png").get_image_data(),
        pyglet.image.load("images/sand.png").get_image_data(),
        pyglet.image.load("images/wool_colored_blue.png").get_image_data()
    ]

    texture_atlas = pyglet.image.atlas.TextureAtlas(width=32, height=32)

    for image in images:
        texture_atlas.add(image)

    global texture
    texture = texture_atlas.texture

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    global window, keys
    window = CameraWindow()
    keys = key.KeyStateHandler()
    window.push_handlers(keys)

    pyglet.app.run()


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
            self.buffers[buffer] = GLuint(0)
            glGenBuffers(1, self.buffers[buffer])
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers[buffer])
            glBufferData(GL_ARRAY_BUFFER, self.buffer_size, None, GL_DYNAMIC_DRAW)

    def data(self, buffer_type, data, offset):
        if buffer_type != "texture":
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers[buffer_type])

            if buffer_type == "color":
                offset *= 16
            else:
                offset *= 12

            gl_data = to_gl_float(data)
            glBufferSubData(GL_ARRAY_BUFFER, offset, sizeof(gl_data), gl_data)

            if buffer_type == "vertex":
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
    x, y, z = 0, chunk_height + height_offset - 5, 0
    rx, ry = 340, 0
    w, h = window_width, window_height
    far = 8192
    fov = 90

    vx, vy, vz = 0, 0, 0

    speed_mult = 5
    jump_height = 5
    camera_height = 1.7
    range = 5
    velocity = (0, 0, 0)

    world_pos = None
    current_chunk = (0, 0)
    current_tile = (0, y, 0)
    modelview = None

    last_pos = None

    flying = False
    jumping = False

    holding_block = 1

    ui = VBO(size=1000)
    text = pyglet.graphics.Batch()

    last_chunk_written = current_chunk
    last_tile_written = current_tile
    last_world_pos_written = (0, y, 0)
    last_rotation_written = (rx, ry)
    last_velocity_written = (vx, vy, vz)

    document = None
    layout = None

    document_offsets = {}

    def view(self, width, height):
        self.w, self.h = width, height
        glViewport(0, 0, width, height)
        self.perspective()

    def perspective(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.w / self.h, 0.1, self.far)
        glMatrixMode(GL_MODELVIEW)

    def ui_mode(self):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(-self.w / 2, self.w / 2, -self.h / 2, self.h / 2)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def init_ui(self):
        self.ui.data("texture", texture, 0)

        vertices, colors, tex_coords = [], [], []

        add_rect(704, 449, 32, 2, (1.0, 1.0, 1.0, 1.0), vertices, colors, tex_coords)
        add_rect(719, 434, 2, 32, (1.0, 1.0, 1.0, 1.0), vertices, colors, tex_coords)
        add_rect(704, 200, 32, 32, (1.0, 1.0, 1.0, 1.0), vertices, colors, tex_coords, image=self.holding_block)

        self.ui.data("vertex", to_gl_float(vertices), 0)
        self.ui.data("color", to_gl_float(colors), 0)
        self.ui.data("texture_coords", to_gl_float(tex_coords), 0)

    def update_ui(self):
        vertices, colors, tex_coords = [], [], []

        add_rect(704, 200, 32, 32, (1.0, 1.0, 1.0, 1.0), vertices, colors, tex_coords, image=self.holding_block)

        self.ui.data("vertex", to_gl_float(vertices), 24)
        self.ui.data("color", to_gl_float(colors), 24)
        self.ui.data("texture_coords", to_gl_float(tex_coords), 24)

    def init_text(self):
        world_pos = (int(self.world_pos[0]), int(self.world_pos[1]), int(self.world_pos[2]))
        rotation = (int(self.rx), int(self.ry))
        velocity = (int(self.velocity[0]), int(self.velocity[1]), int(self.velocity[2]))

        self.document = pyglet.text.decode_text("Chunk: " + str(self.current_chunk) + "\n")
        self.document.insert_text(8 + len(str(self.current_chunk)), "Tile: " + str(self.current_tile) + "\n")
        self.document.insert_text(16 + len(str(self.current_chunk)) + len(str(self.current_tile)),
                                  "World Position: " + str(world_pos) + "\n\n")
        self.document.insert_text(34 + len(str(self.current_chunk)) + len(str(self.current_tile)) + len(str(world_pos)),
                                  "Rotation: " + str(rotation) + "\n")
        self.document.insert_text(45 + len(str(self.current_chunk)) + len(str(self.current_tile)) + len(str(world_pos)) + len(str(rotation)),
                                  "Velocity: " + str(velocity))

        self.document.set_style(0, -1, dict(color=(255, 255, 255, 255)))

        self.layout = pyglet.text.layout.TextLayout(self.document, width=300, height=300, multiline=True, batch=self.text)
        self.layout.x = -(window_width / 2) + 50
        self.layout.y = window_height / 4 - 120

    def update_text_offsets(self):
        elements_to_update = []
        world_pos = (int(self.world_pos[0]), int(self.world_pos[1]), int(self.world_pos[2]))
        rotation = (int(self.rx), int(self.ry))
        velocity = (round(self.velocity[0], 3), round(self.velocity[1], 3), round(self.velocity[2], 3))

        chunk_start = 7
        tile_start = chunk_start + 7 + len(str(self.current_chunk))
        world_pos_start = tile_start + 17 + len(str(self.current_tile))
        rotation_start = world_pos_start + 11 + len(str(world_pos))
        velocity_start = rotation_start + 11 + len(str(rotation))

        self.document_offsets['chunk'] = [chunk_start,
                                          chunk_start + len(str(self.last_chunk_written))]
        self.document_offsets['tile'] = [tile_start,
                                         tile_start + len(str(self.last_tile_written))]
        self.document_offsets['world_pos'] = [world_pos_start,
                                              world_pos_start + len(str(self.last_world_pos_written))]
        self.document_offsets['rotation'] = [rotation_start,
                                             rotation_start + len(str(self.last_rotation_written))]
        self.document_offsets['velocity'] = [velocity_start,
                                             velocity_start + len(str(self.last_velocity_written))]

        if self.last_chunk_written != self.current_chunk:
            self.last_chunk_written = self.current_chunk
            elements_to_update.append(('chunk', str(self.current_chunk)))

        if self.last_tile_written != self.current_tile:
            self.last_tile_written = self.current_tile
            elements_to_update.append(('tile', str(self.current_tile)))

        if self.last_world_pos_written != world_pos:
            self.last_world_pos_written = world_pos
            elements_to_update.append(('world_pos', str(world_pos)))

        if self.last_rotation_written != rotation:
            self.last_rotation_written = rotation
            elements_to_update.append(('rotation', str(rotation)))

        if self.last_velocity_written != velocity:
            self.last_velocity_written = velocity
            elements_to_update.append(('velocity', str(velocity)))

        return elements_to_update

    def draw_text(self):
        elements = self.update_text_offsets()

        if len(elements) > 0:
            self.layout.begin_update()

            for element, value in elements:
                self.document.delete_text(*self.document_offsets[element])
                self.document.insert_text(self.document_offsets[element][0], value)

            self.layout.end_update()

        self.text.draw()

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
            time.get("all")

            get_function_avg()

            pyglet.app.exit()

    def mouse_click(self, x, y, button, modifiers):
        hit = self.hitscan()

        if hit is not None and hit[0] is not None and hit[1] is not None:
            if button == 1:
                chunks[hit[0]].remove_block(hit[1])
            elif button == 4 and len(hit) == 3:
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
        glGetFloatv(GL_MODELVIEW_MATRIX, modelview)
        self.modelview = [[modelview[w + h * 4] for w in range(4)] for h in range(4)]

        self.world_pos = numpy.dot([0, 0, 0, 1], numpy.linalg.inv(self.modelview))[:3]
        self.current_chunk, self.current_tile = get_chunk_pos(self.world_pos)

    def hitscan(self):
        last_pos = None

        for offset in numpy.arange(-1, -self.range, -0.1):
            checking_pos = numpy.dot([0, 0, offset, 1], numpy.linalg.inv(self.modelview))
            checking_chunk, checking_tile = get_chunk_pos(checking_pos)

            sx, sy, sz = checking_tile

            if checking_chunk in active_chunks:
                if checking_tile in chunks[checking_chunk].blocks:
                    if last_pos is not None and get_chunk_pos(last_pos) is not None:
                        return checking_chunk, checking_tile, get_chunk_pos(last_pos)
                    else:
                        return checking_chunk, checking_tile

            last_pos = checking_pos

    def check_player_col(self, tile=None, chunk=None):
        if tile is None:
            tile = self.current_tile

        if chunk is None:
            chunk = self.current_chunk

        roof_colliding = chunks[chunk].block_map[tile[0]][int(self.y) + 1][tile[2]] > 0
        head_colliding = chunks[chunk].block_map[tile[0]][int(self.y)][tile[2]] > 0
        body_colliding = chunks[chunk].block_map[tile[0]][int(self.y) - 1][tile[2]] > 0
        ground_colliding = chunks[chunk].block_map[tile[0]][int(self.y) - 2][tile[2]] > 0

        return roof_colliding, head_colliding, body_colliding, ground_colliding

    def update(self, dt):
        self.get_world_pos()

        if dt >= 0.1:
            return

        try:
            self.key_loop(dt)
        except NameError:
            pass

        if not self.flying and self.current_chunk in active_chunks:
            if 2 <= self.y < chunk_height + height_offset:
                new_chunk, new_tile = get_chunk_pos((self.world_pos[0] + self.vx,
                                                     self.world_pos[1] + self.vy * dt,
                                                     self.world_pos[2] + self.vz))
                roof_col, head_col, body_col, ground_col = self.check_player_col(tile=new_tile, chunk=new_chunk)

                if not head_col and not body_col:
                    self.last_pos = self.world_pos

                    if ground_col:
                        self.vy = 0
                        self.jumping = False

                        if keys[key.SPACE]:
                            self.vy += self.jump_height
                            self.jumping = True
                        else:
                            if self.y - (int(self.y) + 0.7) >= 0.05:
                                self.vy -= 100 * dt
                    else:
                        self.vy -= 9.82 * dt

                elif body_col or head_col:
                    if body_col and head_col:
                        self.vy = 0

                    dx = abs(new_tile[0] - self.current_tile[0])
                    dz = abs(new_tile[2] - self.current_tile[2])

                    if dx != 0:
                        self.vx = 0

                    if dz != 0:
                        self.vz = 0

                    if not self.jumping and keys[key.SPACE]:
                        self.jumping = True
                        self.vy += self.jump_height

                if roof_col:
                    if self.vy > 0:
                        self.vy = 0
            else:
                self.vy -= 9.82 * dt
        else:
            self.vy = 0

        self.velocity = (self.vx, self.vy, self.vz)

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
        self.blocks = set()

        self.offset = 0

        self.block_map = numpy.zeros((chunk_size, chunk_height + height_offset, chunk_size), dtype=numpy.uint8)
        self.offsets = numpy.zeros((chunk_size, chunk_height + height_offset, chunk_size), dtype=numpy.uint32)

        self.is_meshed = False

    def generate(self):
        for sx in range(chunk_size):
            x = sx + self.cx * chunk_size

            for sz in range(chunk_size):
                z = sz + self.cz * chunk_size

                noise_height = noise.snoise3(x / zoom, z / zoom, seed, octaves=3)
                height = round((noise_height + 1) / 2 * chunk_height) + height_offset

                block_id = None

                if 0.66 <= noise_height <= 1.0:
                    block_id = 1

                elif -0.11 <= noise_height < 0.66:
                    block_id = 2

                elif -0.33 <= noise_height < -0.11:
                    block_id = 3

                elif -1.0 <= noise_height < -0.33:
                    block_id = 4

                for y in range(height - 2, height + 1):
                    self.blocks.add((sx, y, sz))

                self.block_map[sx, 0:height + 1, sz] = block_id

    def mesh(self):
        if not self.is_meshed:
            for gx in [-1, 0, 1]:
                for gz in [-1, 0, 1]:
                    chunk_pos = (self.cx + gx, self.cz + gz)

                    if chunk_pos != (self.cx, self.cz) and chunk_pos not in chunks:
                        chunks[chunk_pos] = Chunk(chunk_pos)
                        chunks[chunk_pos].generate()

        self.vbo.data("texture", texture, 0)

        data = ([], [], [], [])
        data_names = ["vertex", "color", "normal", "texture_coords"]

        for pos in self.blocks.copy():
            self.create_block(pos, external_data=data)

        for i, data_list in enumerate(data):
            self.vbo.data(data_names[i], data_list, 0)

        self.is_meshed = True

    def get_color(self, tile):
        self.vbo.color()
        offset = self.offsets.item(tile)

        data = to_gl_float([0] * 4)
        glGetBufferSubData(GL_ARRAY_BUFFER, offset * 16, 16, data)

        return list(data)

    def set_color(self, tile, color):
        offset = self.offsets.item(tile)
        length = (6 - len(self.get_neighbors(tile))) * 4

        self.vbo.data("color", [*color] * length, offset)

    def get_neighbors(self, tile, get_faces=False, local_chunk=False):
        x, y, z = tile

        neighbors = [
            (x - 1, y, z), (x + 1, y, z),
            (x, y - 1, z), (x, y + 1, z),
            (x, y, z + 1), (x, y, z - 1)
        ]

        tile_neighbors = []

        for neighbor in neighbors:
            sx, sy, sz = neighbor
            cx, cz = self.cx, self.cz

            if sx < 0:
                sx += 16
                cx -= 1
            elif sx > 15:
                sx -= 16
                cx += 1

            if sz < 0:
                sz += 16
                cz -= 1
            elif sz > 15:
                sz -= 16
                cz += 1

            if local_chunk and (cx, cz) != (self.cx, self.cz):
                continue

            value = chunks[(cx, cz)].block_map.item((sx, sy, sz))

            if get_faces:
                if value > 0:
                    tile_neighbors.append(1)
                else:
                    tile_neighbors.append(0)
            else:
                if value > 0:
                    tile_neighbors.append(((cx, cz), (sx, sy, sz)))

        return tile_neighbors

    def remove_block(self, tile):
        self.blocks.remove(tile)
        self.block_map.itemset(tile, 0)
        self.offsets.itemset(tile, 0)

        self.vbo = VBO()
        self.offset = 0

        chunk_list = []

        for chunk, neighbor in self.get_neighbors(tile):
            if chunk != (self.cx, self.cz):
                chunk_list.append(chunk)

            if neighbor not in chunks[chunk].blocks:
                chunks[chunk].blocks.add(neighbor)
                chunks[chunk].block_map.itemset(neighbor, 2)

        self.mesh()

        if len(chunk_list) > 0:
            for chunk in chunk_list:
                chunks[chunk].vbo = VBO()
                chunks[chunk].offset = 0
                chunks[chunk].mesh()

    def create_block(self, tile, new=None, external_data=None):
        data_names = ["vertex", "color", "normal", "texture_coords"]

        if external_data is None:
            data = ([], [], [], [])

            if self.add_block(tile, data, new=new):
                offset = self.offsets.item(tile)

                for i, data_list in enumerate(data):
                    self.vbo.data(data_names[i], data_list, offset)
        else:
            self.add_block(tile, external_data, new=new)

    def add_block(self, tile, data, new=None):
        x = tile[0] + self.cx * chunk_size
        z = tile[2] + self.cz * chunk_size

        if new is not None:
            texture_id = new
            self.blocks.add(tile)
            self.block_map.itemset(tile, texture_id)
        else:
            texture_id = self.block_map.item(tile)

        neighbors = self.get_neighbors(tile, get_faces=True)

        if sum(neighbors) == 6 or sum(neighbors) == 0:
            self.blocks.remove(tile)
            return False

        for i, face in enumerate(neighbors):
            if face == 0:
                add_face((x, tile[1], z), i, texture_id, *data)

        self.offsets.itemset(tile, self.offset)
        self.offset += (6 - sum(neighbors)) * 4
        return True


# noinspection PyCallingNonCallable
def to_gl_float(data):
    return (GLfloat * len(data))(*data)


def get_chunk_pos(pos):
    chunk = (int(math.floor(pos[0] / chunk_size)), int(math.floor(pos[2] / chunk_size)))
    tile = (int(pos[0] - chunk[0] * chunk_size), int(pos[1]), int(pos[2] - chunk[1] * chunk_size))

    return chunk, tile


def add_face(pos, face, texture_name, verts, cols, norms, texts, scale=(1.0, 1.0, 1.0)):
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

    for tx, ty, tz in texture_coords[face]:
        tex_coords.append(texture_positions[tx][0])
        tex_coords.append(texture_positions[ty][1] * h)
        tex_coords.append(tz)

    for i, (sx, sy, sz) in enumerate(cube_signs[face]):
        vertices.extend([x + (w * sx), y + (h * sy), z + (d * sz)])
        colors.extend([*texture_color[texture_name]])
        normals.extend([*cube_normals[face]])

    verts.extend(vertices)
    cols.extend(colors)
    norms.extend(normals)
    texts.extend(tex_coords)


def add_rect(x, y, w, h, color, verts, cols, texts, image=None):
    x -= window_width / 2
    y -= window_height / 2

    verts.extend([x + w, y + h, 0, x + w, y, 0, x, y, 0, x, y + h, 0])
    cols.extend([*color] * 4)

    if image:
        texture_position = texture_pos[image]

        texture_positions = [
            [(texture_position[0] * 16) / texture.width, (texture_position[1] * 16) / texture.height],
            [((texture_position[0] + 1) * 16) / texture.width, ((texture_position[1] + 1) * 16) / texture.height]
        ]

        texts.extend([
            texture_positions[0][0], texture_positions[0][1], 0,
            texture_positions[1][0], texture_positions[0][1], 0,
            texture_positions[1][0], texture_positions[1][1], 0,
            texture_positions[0][0], texture_positions[1][1], 0,
        ])
    else:
        texts.extend([0] * 12)


def render_light(pos, direction, angle, attenuation=0):
    glLightfv(GL_LIGHT0, GL_AMBIENT, to_gl_float((0.2, 0.2, 0.2, 1.0)))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, to_gl_float((1.0, 1.0, 1.0, 1.0)))
    glLightfv(GL_LIGHT0, GL_SPECULAR, to_gl_float((0.5, 0.5, 0.5, 1.0)))

    glLightfv(GL_LIGHT0, GL_POSITION, to_gl_float((*pos, attenuation)))
    glLightfv(GL_LIGHT0, GL_SPOT_CUTOFF, to_gl_float([angle]))
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, to_gl_float(direction))

    glEnable(GL_LIGHT0)


def check_draw_distance(chunk):
    active_chunks.clear()

    for cx in range(chunk[0] - render_distance, chunk[0] + render_distance + 1):
        for cz in range(chunk[1] - render_distance, chunk[1] + render_distance + 1):
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
        self.cam.init_text()

        pyglet.clock.schedule_interval(self.cam.update, 1 / 60)

    def on_draw(self):
        glClearColor(0.5, 0.69, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.cam.apply()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_CULL_FACE)

        render_light((0, 100, 0), (0.4, -0.824, 0.4), 45)

        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)

        check_draw_distance(self.cam.current_chunk)

        for chunk in active_chunks:
            chunks[chunk].vbo.draw()

        self.cam.ui_mode()

        self.cam.ui.draw()
        self.cam.draw_text()

        self.cam.perspective()
        self.cam.apply()

init()
