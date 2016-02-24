from ctypes import *

from pyglet.gl import *


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
