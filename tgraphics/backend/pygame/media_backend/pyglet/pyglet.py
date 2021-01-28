import pyglet
from pyglet.gl import *
import os
from pathlib import Path
import sys

from ...pygame import Texture, current_renderer

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

from . import _player_patch

class Player:
    def __init__(self):
        self._image = None
        self._player = _player_patch.PatchedPlayer(self)

    def play(self, window):
        self._player.play(window=window)

    def append(self, source):
        self._player.queue(source._source)

    @property
    def source(self):
        return Source(self._player.source)

    @property
    def texture(self):
        texture = self._image
        if not texture:
            return None
        img_data = texture.get_image_data().get_data('RGBA')
        return Texture.from_str(current_renderer(), bytes(img_data), (texture.width, texture.height), 'RGBA')


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
        format = self._source.video_format
        if format:
            return (format.width, format.height)
        return (0, 0)
