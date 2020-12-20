import itertools
from typing import NamedTuple, Optional, Union
from pygame import Rect

from ...core.backend_loader import _current_backend
from ...core.elementABC import ElementABC

import sys
assert sys.version_info[0] == 3
if sys.version_info[1] < 9:
    from typing import Iterator, List, Tuple
else:
    from collections.abc import Iterator
    List = list
    Tuple = tuple

class Subelement:
    element: ElementABC
    offset: Tuple[int, int]

    def __init__(self, element, offset):
        self.element = element
        self.offset = offset

    def __iter__(self):
        return iter((self.element, self.offset))

    def __getitem__(self, value):
        if value == 0:
            return self.element
        elif value == 1:
            return self.offset
        else:
            raise IndexError('index out of range')

    def __setitem__(self, value, item):
        if value == 0:
            self.element = item
        elif value == 1:
            self.offset = item
        else:
            raise IndexError('index out of range')

class Grid(ElementABC):
    _sub: List[Subelement]
    _mouse_target: Optional[Subelement]
    _mouse_enter: Optional[Subelement]
    _mouse_press: Optional[Subelement]
    _element_target: Optional[Subelement]
    _element_enter: Optional[Subelement]

    def __init__(self, size):
        super().__init__()
        self._sub = list()
        self._loc = (0, 0)
        self._sz = size
        self._mouse_target = None
        self._mouse_enter = None
        self._mouse_press = None
        self._element_target = None
        self._element_enter = None
        # TODO: decorator and some metaclass shenanigans?
        self._listener_dict = {
            'on_position_changed': self._on_child_position_changed,
            'on_this_dropped': self._on_child_this_dropped,
            'on_this_undropped': self._on_child_this_undropped,
            'on_this_dragged': self._on_child_this_dragged
        }

        @self.event
        def on_mouse_motion(x, y, dx, dy): # pylint: disable=unused-variable
            found = False
            for sub, pos in self.elements_at(x, y, actual_loc=True):
                if not found:
                    self._mouse_target = sub
                    found = True
                if self._mouse_enter is sub:
                    sub.element.dispatch('on_mouse_motion', *pos, dx, dy)
                    return True
                if self._mouse_enter is not sub:
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
        def on_element_motion(x, y, element): # pylint: disable=unused-variable
            found = False
            for sub, pos in self.elements_at(x, y, actual_loc=True):
                if not found:
                    self._element_target = sub
                    found = True
                if self._element_enter is sub:
                    sub.element.dispatch('on_element_motion', *pos, element)
                    return True
                if self._element_enter is not sub:
                    if any([sub.element.dispatch('on_element_enter', element), sub.element.dispatch('on_element_motion', *pos, element)]):
                        if self._element_enter:
                            self._element_enter.element.dispatch('on_element_leave', element)
                        self._element_enter = sub
                        return True

            if not found:
                if self._element_enter:
                    self._element_enter.element.dispatch('on_element_leave', element)
                self._element_target = None
                self._element_enter = None
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
        def on_element_leave(element): # pylint: disable=unused-variable
            val = False
            if self._element_enter:
                val = self._element_enter.element.dispatch('on_element_leave', element)
                self._element_enter = None
            return val

        @self.event
        def on_mouse_drag(x, y, dx, dy, buttons): # pylint: disable=unused-variable
            return self._dispatch(self._mouse_press, 'on_mouse_drag', x, y, dx, dy, buttons)

        @self.event
        def on_mouse_press(x, y, button, mods, first): # pylint: disable=unused-variable
            if self._mouse_press:
                self._dispatch(self._mouse_press, 'on_mouse_press', x, y, button, mods, first=False)
                return True
            elif self._mouse_target and first:
                self._mouse_press = self._try_dispatch('on_mouse_press', x, y, button, mods, first=True)
                if self._mouse_press:
                    if self._mouse_press is not self._mouse_enter:
                        self._mouse_enter.element.dispatch('on_mouse_leave')
                        self._mouse_enter = None
                    return True

            return False

        @self.event
        def on_mouse_release(x, y, button, mods, last): # pylint: disable=unused-variable
            if not self._mouse_press:
                return False

            self._dispatch(self._mouse_press, 'on_mouse_release', x, y, button, mods, last=last)

            if last:
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
        def on_element_dropped(x, y, element):
            if self._element_target:
                self._element_target = None
                self._element_enter = None
                return self._try_dispatch('on_element_dropped', x, y, element)

            return False

        @self.event
        def on_element_undropped(x, y, element):
            if self._element_target:
                self._element_target = None
                self._element_enter = None
                return self._try_dispatch('on_element_undropped', x, y, element)

            return False

        @self.event
        def on_mouse_scroll(x, y, dx, dy): # pylint: disable=unused-variable
            if self._mouse_press:
                self._dispatch(self._mouse_press, 'on_mouse_scroll', x, y, dx, dy)
                return True
            if self._mouse_target and self._try_dispatch('on_mouse_scroll', x, y, dx, dy):
                return True
            
            return False

    def elements_at(self, x, y, actual_loc=False, after=None) -> Iterator[Tuple[Subelement, Tuple[int, int]]]:
        """
        get all elements from top to bottom at x, y
        """
        if actual_loc:
            _req_loc = (x + self._loc[0], y + self._loc[1])
        else:
            _req_loc = (x, y)
        if after:
            _found = False
        else:
            _found = True
        for sub in reversed(self._sub):
            if _found:
                _sub_loc = (_req_loc[0] - sub.offset[0], _req_loc[1] - sub.offset[1])
                if 0 <= _sub_loc[0] and 0 <= _sub_loc[1]:
                    _sz = sub.element.size
                    if _sub_loc[0] <= _sz[0] and _sub_loc[1] <= _sz[1]:
                        yield sub, _sub_loc
                continue
            
            if sub is after or sub.element is after:
                _found = True

    def _dispatch(self, sub: Optional[Subelement], event, x, y, *args, **kwargs):
        if sub:
            return sub.element.dispatch(event, x + self._loc[0] - sub.offset[0], y + self._loc[1] - sub.offset[1], *args, **kwargs)
        else:
            return False

    def _try_dispatch(self, event, x, y, *args, _dispatch_after=None, _tries=None, **kwargs):
        tries = range(_tries) if _tries else itertools.count()
        for (sub, pos), _ in zip(self.elements_at(x, y, actual_loc=True, after=_dispatch_after), tries):
            if sub.element.dispatch(event, *pos, *args, **kwargs):
                return sub

        return None

    def _on_child_position_changed(self, dx, dy, child):
        match = next(sub for sub in self._sub if sub.element is child)
        n_off = match.offset
        match.offset = (n_off[0] + dx, n_off[1] + dy)
        return True

    def _on_child_this_dropped(self, this):
        match = next((sub for sub in self._sub if sub.element is this), None)
        if match:
            n_off = match.offset
            sz = this.size
            child_pos = (n_off[0] + (sz[0]/2), n_off[1] + (sz[1]/2))
            if self._try_dispatch('on_element_dropped', *child_pos, this, _dispatch_after=this) is not self._element_enter:
                if self._element_enter:
                    self._element_enter.element.dispatch('on_element_leave', this)
            self._element_enter = None
        return True

    def _on_child_this_undropped(self, this):
        match = next((sub for sub in self._sub if sub.element is this), None)
        if match:
            n_off = match.offset
            sz = this.size
            child_pos = (n_off[0] + (sz[0]/2), n_off[1] + (sz[1]/2))
            if self._try_dispatch('on_element_undropped', *child_pos, this, _dispatch_after=this) is not self._element_enter:
                if self._element_enter:
                    self._element_enter.element.dispatch('on_element_leave', this)
            self._element_enter = None
        return True

    def _on_child_this_dragged(self, this):
        match = next((sub for sub in self._sub if sub.element is this), None)
        if match:
            n_off = match.offset
            sz = this.size
            child_pos = (n_off[0] + (sz[0]/2), n_off[1] + (sz[1]/2))
            for sub, pos in self.elements_at(*child_pos, actual_loc=True, after=this):
                if sub is self._element_enter:
                    self._dispatch(sub, 'on_element_motion', *child_pos, this)
                    break
                elif sub.element.dispatch('on_element_enter', this):
                    if self._element_enter:
                        self._element_enter.element.dispatch('on_element_leave', this)
                    self._element_enter = sub
                    break
            else:
                if self._element_enter:
                    self._element_enter.element.dispatch('on_element_leave', this)
                self._element_enter = None

        return True

    def _add_listeners(self, child: ElementABC):
        for e, h in self._listener_dict.items():
            child.event[e].add_listener(h)

    def _remove_listeners(self, child: ElementABC):
        for e, h in self._listener_dict.items():
            child.event[e].remove_listener(h)

    def add_child(self, index, child: ElementABC, position):
        """
        add a child element

        note: adding the same element which its position may change might result in an unexpected behavior
        """
        self._add_listeners(child)
        self._sub.insert(index, Subelement(child, position))

    def add_child_top(self, child: ElementABC, position):
        """
        add a child element on top

        note: adding the same element which its position may change might result in an unexpected behavior
        """
        self._add_listeners(child)
        self._sub.append(Subelement(child, position))

    def remove_child(self, child: Union[int, ElementABC, Subelement]):
        if isinstance(child, Subelement):
            self._sub.remove(child)
        elif isinstance(child, int):
            child = self._sub.pop(child)
        else:
            assert isinstance(child, ElementABC), 'unrecognized grid.remove_child child argument type'
            # construction via comprehensions should be the fastest way to do this in just Python
            _idx = {i for i, sub in enumerate(self._sub) if sub.element is child}
            childs = [sub for i, sub in enumerate(self._sub) if i not in _idx]
            self._sub = [sub for i, sub in enumerate(self._sub) if i not in _idx]
            for child in childs:
                self._remove_listeners(child.element)
            return
        
        self._remove_listeners(child.element)

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
            x, y = pos
            if x <= self._loc[0] + self._sz[0] and y <= self._loc[1] + self._sz[1] and x + _sz[0] >= self._loc[0] and y + _sz[1] >= self._loc[1]:
                c.render((location[0] + x, location[1] + y), None if not size else (size[0] / self._sz[0] * _sz[0], size[1] / self._sz[1] * _sz[1]))
