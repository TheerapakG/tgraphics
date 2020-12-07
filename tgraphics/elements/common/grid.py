from typing import List, Optional, Tuple, Union
from pygame import Rect

from ...core.backend_loader import _current_backend
from ...core.elementABC import ElementABC

class Subelement:
    def __init__(self, element: ElementABC, offset: Tuple[int, int]):
        self.element = element
        self.offset = offset

class Grid(ElementABC):
    _sub: List[Subelement]
    _mouse_target: Optional[Subelement]
    _mouse_enter: Optional[Subelement]
    _mouse_press: Optional[Subelement]

    def __init__(self, size):
        super().__init__()
        self._sub = list()
        self._loc = (0, 0)
        self._sz = size
        self._mouse_target = None
        self._mouse_enter = None
        self._mouse_press = None

        @self.event
        def on_mouse_motion(x, y, dx, dy): # pylint: disable=unused-variable
            found = False
            for sub, pos in self.elements_at(x, y, actual_loc=True):
                if not found:
                    self._mouse_target = sub
                    found = True
                if self._mouse_enter is not sub:
                    entered = False
                    if any([sub.element.dispatch('on_mouse_enter'), sub.element.dispatch('on_mouse_motion', *pos, dx, dy)]):
                        if self._mouse_enter:
                            self._mouse_enter.element.dispatch('on_mouse_leave')
                        self._mouse_enter = sub
                        return True

            if not found:
                if self._mouse_enter:
                    self._mouse_enter.element.dispatch('on_mouse_leave')
                self._mouse_target = None
                self._mouse_enter = None
                return True
            return False

        @self.event
        def on_mouse_leave(): # pylint: disable=unused-variable
            val = False
            if self._mouse_enter:
                val = self._mouse_enter.element.dispatch('on_mouse_leave')
                self._mouse_enter = None
            return val

        @self.event
        def on_mouse_drag(x, y, dx, dy, buttons): # pylint: disable=unused-variable
            return self._dispatch(self._mouse_press, 'on_mouse_drag', x, y, dx, dy, buttons)

        @self.event
        def on_mouse_press(x, y, button, mods): # pylint: disable=unused-variable
            if self._mouse_press:
                self._dispatch(self._mouse_press, 'on_mouse_press', x, y, button, mods)
                return True
            if self._mouse_target:
                if self._mouse_press := self._try_dispatch('on_mouse_press', x, y, button, mods):
                    if self._mouse_press is not self._mouse_enter:
                        self._mouse_enter.element.dispatch('on_mouse_leave')
                        self._mouse_enter = None
                    return True
            return False

        @self.event
        def on_mouse_release(x, y, button, mods): # pylint: disable=unused-variable
            if not self._mouse_press:
                return False

            self._dispatch(self._mouse_press, 'on_mouse_release', x, y, button, mods)
            if _current_backend().mouse.pressed() == _current_backend().mouse.NButton:
                self._mouse_press = None
                found = False
                for sub, pos in self.elements_at(x, y, actual_loc=True):
                    if not found:
                        self._mouse_target = sub
                        found = True
                    if self._mouse_enter is sub:
                        return True
                    elif sub.element.dispatch('on_mouse_enter'):
                        if self._mouse_enter:
                            self._mouse_enter.element.dispatch('on_mouse_leave')
                        self._mouse_enter = sub
                        return True
                
                if self._mouse_enter:
                    self._mouse_enter.dispatch('on_mouse_leave')
                    self._mouse_enter = None

                if not found:
                    self._mouse_target = None

                return True

        @self.event
        def on_mouse_scroll(x, y, dx, dy): # pylint: disable=unused-variable
            if self._mouse_press:
                self._dispatch(self._mouse_press, 'on_mouse_scroll', x, y, dx, dy)
                return True
            if self._mouse_target and self._try_dispatch('on_mouse_scroll', x, y, dx, dy):
                return True
            
            return False

    def elements_at(self, x, y, actual_loc = False) -> Tuple[Subelement, Tuple[int, int]]:
        """
        get all elements from top to bottom at x, y
        """
        if actual_loc:
            _req_loc = (x + self._loc[0], y + self._loc[1])
        else:
            _req_loc = (x, y)
        for sub in reversed(self._sub):
            _sub_loc = (_req_loc[0] - sub.offset[0], _req_loc[1] - sub.offset[1])
            if 0 <= _sub_loc[0] and 0 <= _sub_loc[1]:
                _sz = sub.element.size
                if _sub_loc[0] <= _sz[0] and _sub_loc[1] <= _sz[1]:
                    yield sub, _sub_loc

    def _dispatch(self, sub: Optional[Subelement], event, x, y, *args, **kwargs):
        if sub:
            return sub.element.dispatch(event, x + self._loc[0] - sub.offset[0], y + self._loc[1] - sub.offset[1], *args, **kwargs)
        else:
            return False

    def _try_dispatch(self, event, x, y, *args, **kwargs):
        for sub, pos in self.elements_at(x, y, actual_loc=True):
            if sub.element.dispatch('on_mouse_motion', *pos, *args, **kwargs):
                return sub

        return None

    def add_child(self, index, child: ElementABC, position):
        self._sub.insert(index, (child, position))

    def add_child_top(self, child: ElementABC, position):
        self._sub.append((child, position))

    def remove_child(self, child: Union[int, ElementABC]):
        if isinstance(child, ElementABC):
            # construction via comprehensions should be the fastest way to do this in just Python
            _idx = {i for i, sub in enumerate(self._sub) if sub[0] is child}
            self._sub = [sub for i, sub in enumerate(self._sub) if i not in _idx]
        else: # isinstance(child, int)
            assert isinstance(child, int), 'unrecognized grid.remove_child child argument type'
            self._sub.pop(child)

    def remove_child_top(self):
        self._sub.pop()

    def _bound(self):
        all_loc = [Rect(pos, c.size) for c, pos in self._sub]
        return Rect.union(all_loc)

    @property
    def bound(self):
        _b = self._bound()
        return (_b.topleft, _b.bottomright)

    @property
    def size(self):
        return self._sz

    @size.setter
    def size(self, size):
        self._sz = size

    @property
    def view(self):
        _x = self._loc[0] + self._sz[0]
        _y = self._loc[1] + self._sz[1]
        return (self._loc, (_x, _y))

    @view.setter
    def view(self, new_view):
        self._loc = new_view[0]
        if new_view[1]:
            self._sz[0] = new_view[1][0] - new_view[0][0]
            self._sz[1] = new_view[1][1] - new_view[0][1]

    def render(self, location, size=None):
        for c, pos in self._sub:
            _sz = c.size
            x, y = location[0] + pos[0], location[1] + pos[1]
            if x <= self._loc[0] + self._sz[0] and y <= self._loc[1] + self._sz[1] and x + _sz[0] >= self._loc[0] and y + _sz[1] >= self._loc[1]:
                c.render((x, y), None if not size else (size[0] / self._sz[0] * _sz[0], size[1] / self._sz[1] * _sz[1]))
