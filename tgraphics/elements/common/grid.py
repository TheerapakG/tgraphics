from typing import List, Tuple, Union
from pygame import Rect

from ...core.backend_loader import _current_backend
from ...core.elementABC import ElementABC

class Grid(ElementABC):
    _sub: List[Tuple[ElementABC, Tuple[int, int]]]

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
            for c, pos in reversed(self._sub):
                if pos[0] <= x + self._loc[0] and pos[1] <= y + self._loc[1]:
                    _sz = c.size
                    if x + self._loc[0] <= pos[0] + _sz[0] and y + self._loc[1] <= pos[1] + _sz[1]:
                        if not found:
                            self._mouse_target = c
                            found = True
                        if self._mouse_enter is not c:
                            entered = False
                            if c.dispatch('on_mouse_enter'):
                                c.dispatch('on_mouse_motion', x+self._loc[0]-pos[0], y+self._loc[1]-pos[1], dx, dy)
                                entered = True
                            if entered or c.dispatch('on_mouse_motion', x+self._loc[0]-pos[0], y+self._loc[1]-pos[1], dx, dy):
                                if self._mouse_enter:
                                    self._mouse_enter.dispatch('on_mouse_leave')
                                self._mouse_enter = c
                                return True

            if not found:
                if self._mouse_enter:
                    self._mouse_enter.dispatch('on_mouse_leave')
                self._mouse_target = None
                self._mouse_enter = None
                return True
            return False

        @self.event
        def on_mouse_leave(): # pylint: disable=unused-variable
            val = False
            if self._mouse_enter:
                val = self._mouse_enter.dispatch('on_mouse_leave')
                self._mouse_enter = None
            return val

        @self.event
        def on_mouse_drag(x, y, dx, dy, buttons): # pylint: disable=unused-variable
            if self._mouse_press:
                self._mouse_press[0].dispatch('on_mouse_drag', x, y, dx, dy, buttons)
                return True
            
            return False

        @self.event
        def on_mouse_press(x, y, button, mods): # pylint: disable=unused-variable
            if self._mouse_press:
                self._mouse_press[0].dispatch('on_mouse_press', x, y, button, mods)
                return True
            if self._mouse_target:
                if self._mouse_press := self._try_dispatch('on_mouse_press', x, y, button, mods):
                    if self._mouse_press[0] is not self._mouse_enter:
                        self._mouse_enter.dispatch('on_mouse_leave')
                        self._mouse_enter = None
                    return True
            
            return False

        @self.event
        def on_mouse_release(x, y, button, mods): # pylint: disable=unused-variable
            if self._mouse_press:
                self._mouse_press[0].dispatch('on_mouse_release', x, y, button, mods)

                found = False
                if _current_backend().mouse.pressed() == _current_backend().mouse.NButton:
                    for c, pos in reversed(self._sub):
                        if pos[0] <= x + self._loc[0] and pos[1] <= y + self._loc[1]:
                            _sz = c.size
                            if x + self._loc[0] <= pos[0] + _sz[0] and y + self._loc[1] <= pos[1] + _sz[1]:
                                if not found:
                                    self._mouse_target = c
                                    found = True
                                if self._mouse_press[0] is c:
                                    break
                                if self._mouse_press[0] is not c and c.dispatch('on_mouse_enter'):
                                    if self._mouse_enter:
                                        self._mouse_enter.dispatch('on_mouse_leave')
                                        self._mouse_enter = None
                                    self._mouse_enter = c
                                    break
                    else:
                        if self._mouse_enter:
                            self._mouse_enter.dispatch('on_mouse_leave')
                            self._mouse_enter = None

                    if not found:
                        self._mouse_target = None

                    self._mouse_press = None
                return True
            
            return False

        @self.event
        def on_mouse_scroll(x, y, dx, dy): # pylint: disable=unused-variable
            if self._mouse_press:
                self._mouse_press[0].dispatch('on_mouse_scroll', x, y, dx, dy)
                return True
            if self._mouse_target and self._try_dispatch('on_mouse_scroll', x, y, dx, dy):
                return True
            
            return False

    def _try_dispatch(self, event, x, y, *args, **kwargs):
        for c, pos in reversed(self._sub):
            if pos[0] <= x + self._loc[0] and pos[1] <= y + self._loc[1]:
                _sz = c.size
                if x + self._loc[0] <= pos[0] + _sz[0] and y + self._loc[1] <= pos[1] + _sz[1]:
                    if c.dispatch('on_mouse_motion', x+self._loc[0]-pos[0], y+self._loc[1]-pos[1], *args, **kwargs):
                        return c, pos

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
