import datetime
import pyglet
from pyglet.gl import *
import time

from ..pygame import Texture, _current_renderer

class Player:
    def __init__(self):
        self._player = pyglet.media.Player()

    def play(self):
        self._start = time.perf_counter()
        self._player.play()

    def append(self, source):
        self._player.queue(source._source)

    @property
    def source(self):
        return Source(self._player.source)

    @property
    def texture(self):
        pyglet.clock.tick()
        # Download from the driver (opengl), then upload to the driver (whatever SDL is using: 
        # directx, vulkan or even opengl). Truly inefficient.
        texture = self._player.texture
        if not texture:
            return None
        img_data = texture.get_image_data().get_data('RGBA')
        return Texture.from_str(_current_renderer(), bytes(img_data), (texture.width, texture.height), 'RGBA')


class Source:
    def __init__(self, pyglet_source):
        self._source = pyglet_source

    @staticmethod
    def from_file(filename, preload=False):
        media = pyglet.media.load(filename)
        if preload:
            media = pyglet.media.StaticSource(media)
        return Source(media)

    @property
    def size(self):
        return (self._source.video_format.width, self._source.video_format.height)
