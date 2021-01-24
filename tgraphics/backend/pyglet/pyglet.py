import pyglet
from pyglet.gl import *

class Renderer:
    def __init__(self):
        # we only have opengl here so there will only be one renderer object
        self._target = None
        self._batch = pyglet.graphics.Batch()
        self._color = (0, 0, 0, 255)

    @property
    def target(self):
        class _TargetGetProxy:
            def __init__(self, renderer):
                self._renderer = renderer

            def get(self):
                return self._renderer._target

            def __call__(self, new_target):
                class _TargetCtxMgrProxy:
                    def __init__(self, renderer):
                        self._renderer = renderer
                        self._replacing = []

                    def __enter__(self):
                        self._replacing.append(self._target)
                        self._renderer.target = new_target

                    def __exit__(self, type, value, traceback):
                        self._renderer.target = self._replacing.pop()
                
                return _TargetCtxMgrProxy(self._renderer)

        return _TargetGetProxy(self)

    @target.setter
    def target(self, new_target):
        if new_target:
            glDisable(self._target.target)
            glEnable(new_target.target)
            glBindTexture(new_target.target, new_target.id)
            glViewport(0, 0, new_target.width, new_target.height)
            gluOrtho2D(0, new_target.width, new_target.height, 0)
        else:
            glDisable(self._target)
        self._target = new_target

    @property
    def draw_color(self):
        class _ColorGetProxy:
            def __init__(self, renderer):
                self._renderer = renderer

            def get(self):
                return self._renderer._color

            def __call__(self, new_color):
                class _ColorCtxMgrProxy:
                    def __init__(self, renderer):
                        self._renderer = renderer
                        self._replacing = []

                    def __enter__(self):
                        self._replacing.append(self._renderer._color)
                        self._renderer.draw_color = new_color

                    def __exit__(self, type, value, traceback):
                        self._renderer.draw_color = self._replacing.pop()
                
                return _ColorCtxMgrProxy(self._renderer)

        return _ColorGetProxy(self)

    @draw_color.setter
    def draw_color(self, new_color):
        self._renderer._color = new_color

    def clear(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def update(self):
        self._batch.draw()
        self._batch = pyglet.graphics.Batch()

    def draw_line(self, p1, p2):
        pyglet.graphics.Line(*p1, *p2, color=self._color[:3], batch=self._batch).opacity = self._color[3]

    def draw_point(self, point):
        raise NotImplementedError()

    def draw_rect(self, rect):
        raise NotImplementedError()

    def fill_rect(self, rect):
        pyglet.graphics.Rectangle(*rect[0], *rect[1], color=self._color[:3], batch=self._batch).opacity = self._color[3]

# Image is roughly equivalent to Surface in SDL

# Sprite is roughly equivalent to Texture in SDL
