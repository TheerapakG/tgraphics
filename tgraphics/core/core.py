from functools import partial

from .backend_loader import _current_backend

_WindowsBoundedElement = dict()

class Window:
    _current_mouse_interact = None

    @classmethod
    def with_mouse_interaction(cls):
        return cls._current_mouse_interact

    def __init__(self, _back):
        self._window = _back
        self._mouse_target = None

        @self.event
        def on_mouse_press(x, y, button, mods): # pylint: disable=unused-variable
            if not self._current_mouse_interact:
                self._current_mouse_interact = self     
            else:
                assert self._current_mouse_interact is self, "mouse event not locked to a window after clicked"

            return self._mouse_target.dispatch('on_mouse_press', x, y, button, mods)

        @self.event
        def on_mouse_drag(x, y, dx, dy, buttons): # pylint: disable=unused-variable
            assert self._current_mouse_interact is self, "mouse event not locked to a window after clicked"

            if self._mouse_target:
                return self._mouse_target.dispatch('on_mouse_drag', x, y, dx, dy, buttons)
            else:
                return False

        @self.event
        def on_mouse_release(x, y, button, mods): # pylint: disable=unused-variable
            assert self._current_mouse_interact is self, "mouse event not locked to a window after clicked"

            if self._mouse_target:
                return self._mouse_target.dispatch('on_mouse_release', x, y, button, mods)
                if buttons == _current_backend().mouse.NButton:
                    self._mouse_target = None
                    self._current_mouse_interact = None
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

    def icon(self, surface):
        self._window.set_icon(surface)

    icon = property(None, icon)

    @property
    def target_element(self):
        return _WindowsBoundedElement[self]

    @target_element.setter
    def target_element(self, element):
        _WindowsBoundedElement[self] = element
        if element:
            self._window.event('on_draw')(partial(element.render, (0, 0)))
            self._window.target = element
        else:
            self._window.event('on_draw')(None)
            self._window.target = None

    def event(self, func):
        return self._window.event(func)

def run():
    _current_backend().run()
