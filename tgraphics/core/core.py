import asyncio
from functools import partial
import datetime
import time

from .backend_loader import _current_backend

_WindowsBoundedElement = dict()

class Window:
    _current_mouse_interact = None

    @classmethod
    def with_mouse_interaction(cls):
        return cls._current_mouse_interact

    def __init__(self, _back):
        self._window = _back

        @self.event
        def on_mouse_press(x, y, button, mods, first): # pylint: disable=unused-variable
            if not self._current_mouse_interact:
                self._current_mouse_interact = self     
            else:
                assert self._current_mouse_interact is self, "mouse event not locked to a window after clicked"

            if self.target_element:
                return self.target_element.dispatch('on_mouse_press', x, y, button, mods, first=first)
            else:
                return False

        @self.event
        def on_mouse_drag(x, y, dx, dy, buttons): # pylint: disable=unused-variable
            assert self._current_mouse_interact is self, "mouse event not locked to a window after clicked"

            if self.target_element:
                return self.target_element.dispatch('on_mouse_drag', x, y, dx, dy, buttons)
            else:
                return False

        @self.event
        def on_mouse_release(x, y, button, mods, last): # pylint: disable=unused-variable
            assert self._current_mouse_interact is self, "mouse event not locked to a window after clicked"

            if self.target_element:
                return self.target_element.dispatch('on_mouse_release', x, y, button, mods, last=last)
            else:
                return False

    @staticmethod
    def create(title="TGraphics", size=(1280, 720), full_screen=False, resizable=False):
        window = Window(_current_backend().Window.create(title, size, full_screen=full_screen, resizable=resizable))
        _WindowsBoundedElement[window] = None
        return window

    def __hash__(self):
        return hash(self._window)

    def __eq__(self, other):
        if not isinstance(other, Window):
            return NotImplemented
        return self._window == other._window

    def destroy(self):
        del _WindowsBoundedElement[self]
        self._window.destroy()

    @property
    def title(self):
        return self._window.title

    @title.setter
    def title(self, title):
        self._window.title = title

    @property
    def resizable(self):
        return self._window.resizable

    @resizable.setter
    def resizable(self, resizable):
        self._window.resizable = resizable

    @property
    def size(self):
        return self._window.size

    @size.setter
    def size(self, size):
        self._window.size = size

    def icon(self, surface):
        self._window.set_icon(surface)

    icon = property(None, icon)

    def _on_draw(self, element):
        element.render((0, 0))
        self._window.dispatch('on_draw_finished')
        return True

    @property
    def frame_time(self):
        return self._window.frame_time

    @property
    def fps(self):
        return self._window.fps

    @fps.setter
    def fps(self, fps):
        self._window.fps = fps

    @property
    def target_element(self):
        return _WindowsBoundedElement[self]

    @target_element.setter
    def target_element(self, element):
        _WindowsBoundedElement[self] = element
        if element:
            self._window.event('on_draw')(partial(self._on_draw, element))
            self._window.target = element
        else:
            self._window.event('on_draw')(None)
            self._window.target = None

    def event(self, func):
        return self._window.event(func)

def run():
    _current_backend().run()
