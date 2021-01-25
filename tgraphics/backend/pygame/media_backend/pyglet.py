import datetime
from types import MethodType
import pyglet
from pyglet.gl import *
import os
from pathlib import Path
import sys
import time
from ..pygame import Texture, _current_renderer

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
            self._image = None
            # @TheerapakG: a hack to make update_texture store image in memory instead of
            # uploading to the opengl driver
            def update_texture(fself, dt=None):
                """Manually update the texture from the current source.
                This happens automatically, so you shouldn't need to call this method.
                Args:
                    dt (float): The time elapsed since the last call to
                        ``update_texture``.
                """
                source = fself.source
                time = fself.time

                frame_rate = source.video_format.frame_rate
                frame_duration = 1 / frame_rate
                ts = source.get_next_video_timestamp()
                # Allow up to frame_duration difference
                while ts is not None and ts + frame_duration < time:
                    source.get_next_video_frame()  # Discard frame
                    ts = source.get_next_video_timestamp()

                if ts is None:
                    # No more video frames to show. End of video stream.

                    pyglet.clock.schedule_once(fself._video_finished, 0)
                    return

                image = source.get_next_video_frame()
                if image is not None:
                    self._image = image

                ts = source.get_next_video_timestamp()
                if ts is None:
                    delay = frame_duration
                else:
                    delay = ts - time

                delay = max(0.0, delay)
                pyglet.clock.schedule_once(fself.update_texture, delay)

            self._player.update_texture = MethodType(update_texture, self._player)

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
