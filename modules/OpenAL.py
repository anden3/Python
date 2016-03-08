import wave

from pyglet.media.drivers.openal import lib_alc as alc
from pyglet.media.drivers.openal import lib_openal as al


class Listener(object):
    def __init__(self):
        self.device = alc.alcOpenDevice(None)
        self.context = alc.alcCreateContext(self.device, None)
        self._position = (0, 0, 0)
        self._orientation = (0, 0, 0)
        alc.alcMakeContextCurrent(self.context)

    def _set_position(self, pos):
        self._position = pos
        x, y, z = map(int, pos)
        al.alListener3f(al.AL_POSITION, x, y, z)

    def _set_orientation(self, orientation):
        self._orientation = orientation

        # noinspection PyCallingNonCallable
        al_data = (al.ALfloat * 6)(*orientation)
        al.alListenerfv(al.AL_ORIENTATION, al_data)

    def delete(self):
        alc.alcDestroyContext(self.context)
        alc.alcCloseDevice(self.device)

    position = property(None, _set_position)
    orientation = property(None, _set_orientation)


class LoadSound(object):
    def __init__(self, file):
        self.name = file

        wavefp = wave.open(file)
        channels = wavefp.getnchannels()
        bitrate = wavefp.getsampwidth() * 8
        samplerate = wavefp.getframerate()
        wavbuffer = wavefp.readframes(wavefp.getnframes())

        self.duration = (len(wavbuffer) / float(samplerate)) / 2
        self.length = len(wavbuffer)

        formatmap = {
            (1, 8): al.AL_FORMAT_MONO8,
            (2, 8): al.AL_FORMAT_STEREO8,
            (1, 16): al.AL_FORMAT_MONO16,
            (2, 16): al.AL_FORMAT_STEREO16,
        }
        alformat = formatmap[(channels, bitrate)]

        self.buffer = al.ALuint(0)
        al.alGenBuffers(1, self.buffer)
        al.alBufferData(self.buffer, alformat, wavbuffer, self.length, samplerate)

    def delete(self):
        al.alDeleteBuffers(1, self.buffer)


class SoundPlayer(object):
    def __init__(self):
        self.source = al.ALuint(0)
        al.alGenSources(1, self.source)

        al.alSourcef(self.source, al.AL_ROLLOFF_FACTOR, 0)
        al.alSourcei(self.source, al.AL_SOURCE_RELATIVE, 0)

        self.state = al.ALint(0)

        self._volume = 1.0
        self._pitch = 1.0
        self._position = [0, 0, 0]
        self._rolloff = 1.0
        self._loop = False
        self.queue = []

    def _set_rolloff(self, value):
        self._rolloff = value
        al.alSourcef(self.source, al.AL_ROLLOFF_FACTOR, value)

    def _set_loop(self, lo):
        self._loop = lo
        al.alSourcei(self.source, al.AL_LOOPING, lo)

    def _set_position(self, pos):
        self._position = pos
        x, y, z = map(int, pos)
        al.alSource3f(self.source, al.AL_POSITION, x, y, z)

    def _set_pitch(self, pit):
        self._pitch = pit
        al.alSourcef(self.source, al.AL_PITCH, pit)

    def _set_volume(self, vol):
        self._volume = vol
        al.alSourcef(self.source, al.AL_GAIN, vol)

    def _set_seek(self, offset):
        al.alSourcei(self.source, al.AL_BYTE_OFFSET, int(self.queue[0].length * offset))

    def _get_seek(self):
        al.alGetSourcei(self.source, al.AL_BYTE_OFFSET, self.state)
        return float(self.state.value) / float(self.queue[0].length)

    def add(self, sound):
        al.alSourceQueueBuffers(self.source, 1, sound.buffer)
        self.queue.append(sound)

    def remove(self):
        if len(self.queue) > 0:
            al.alSourceUnqueueBuffers(self.source, 1, self.queue[0].buffer)
            al.alSourcei(self.source, al.AL_BUFFER, 0)
            self.queue.pop(0)

    def play(self):
        al.alSourcePlay(self.source)

    def playing(self):
        al.alGetSourcei(self.source, al.AL_SOURCE_STATE, self.state)

        if self.state.value == al.AL_PLAYING:
            return True
        else:
            return False

    def stop(self):
        al.alSourceStop(self.source)

    def rewind(self):
        al.alSourceRewind(self.source)

    def pause(self):
        al.alSourcePause(self.source)

    def delete(self):
        if self.playing():
            self.stop()

        al.alDeleteSources(1, self.source)

    rolloff = property(None, _set_rolloff)
    loop = property(None, _set_loop)
    position = property(None, _set_position)
    pitch = property(None, _set_pitch)
    volume = property(None, _set_volume)
    seek = property(_get_seek, _set_seek)
