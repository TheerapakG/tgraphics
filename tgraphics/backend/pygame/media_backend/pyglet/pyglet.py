import pyglet
from pyglet.gl import *
import os
from pathlib import Path
import sys
from ...pygame import Texture, _current_renderer

# Windows shit
if sys.platform.startswith('win'):
    import ctypes
    _fpath = None
    for _path in os.environ['Path'].split(os.pathsep):
        path = Path(_path)
        if (path/'ffmpeg.exe').exists():
            _fpath = path
            break
        elif (path/'bin'/'ffmpeg.exe').exists():
            _fpath = path/'bin'
            break
    if _fpath:
        ctypes.windll.kernel32.SetDllDirectoryW(str(_fpath))

PATCH_UPLOAD_TEXTURE = True

class Player:
    def __init__(self):
        self._player = pyglet.media.Player()

        if PATCH_UPLOAD_TEXTURE:
            from . import _player_patch
            self._image = None
            _player_patch.patch(self, self._player)

    def play(self):
        self._player.play()

    def append(self, source):
        self._player.queue(source._source)

    @property
    def source(self):
        return Source(self._player.source)

    @property
    def texture(self):
        pyglet.clock.tick()
        if PATCH_UPLOAD_TEXTURE:
            texture = self._image
        else:
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
