import asyncio
from enum import auto, Enum
import itertools
from typing import NamedTuple, Optional, Union
from pygame import Rect

from ...core.backend_loader import _current_backend
from ...core.elementABC import DropNotSupportedError, ElementABC
from ...core.eventdispatch import event_handler

from ...utils.typehint import *

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
        self._mouse_pos = None
        # TODO: decorator and some metaclass shenanigans?
        self._listener_dict = {
            'on_position_changed': self._on_child_position_changed,
            'on_this_dropped': self._on_child_this_dropped,
            'on_this_undropped': self._on_child_this_undropped,
            'on_this_dragged': self._on_child_this_dragged,
            'on_this_request_top': self._on_child_this_request_top,
            'on_this_request_bottom': self._on_child_this_request_bottom,
        }

    @event_handler
    async def on_mouse_motion(self, x, y, dx, dy): # pylint: disable=unused-variable
        self._mouse_pos = (x, y)
        found = False
        for sub, pos in self.elements_at(x, y, actual_loc=True):
            if not found:
                self._mouse_target = sub
                found = True
            if self._mouse_enter is sub:
                await sub.element.dispatch_async('on_mouse_motion', *pos, dx, dy)
                return True
            if self._mouse_enter is not sub:
                if any(await asyncio.gather(
                    sub.element.dispatch_async('on_mouse_enter'), 
                    sub.element.dispatch_async('on_mouse_motion', *pos, dx, dy)
                )):
                    if self._mouse_enter:
                        await self._mouse_enter.element.dispatch_async('on_mouse_leave')
                    self._mouse_enter = sub
                    return True

        if not found:
            if self._mouse_enter:
                await self._mouse_enter.element.dispatch_async('on_mouse_leave')
            self._mouse_target = None
            self._mouse_enter = None
            return True
        return False

    @event_handler
    async def on_element_motion(self, x, y, element): # pylint: disable=unused-variable
        found = False
        for sub, pos in self.elements_at(x, y, actual_loc=True):
            if not found:
                self._element_target = sub
                found = True
            if self._element_enter is sub:
                await sub.element.dispatch_async('on_element_motion', *pos, element)
                return True
            if self._element_enter is not sub:
                if any(await asyncio.gather(
                    sub.element.dispatch_async('on_element_enter', element), 
                    sub.element.dispatch_async('on_element_motion', *pos, element)
                )):
                    if self._element_enter:
                        await self._element_enter.element.dispatch_async('on_element_leave', element)
                    self._element_enter = sub
                    return True

        if not found:
            if self._element_enter:
                await self._element_enter.element.dispatch_async('on_element_leave', element)
            self._element_target = None
            self._element_enter = None
            return True
        return False

    @event_handler
    async def on_mouse_leave(self): # pylint: disable=unused-variable
        self._mouse_pos = None
        val = False
        if self._mouse_enter:
            val = await self._mouse_enter.element.dispatch_async('on_mouse_leave')
            self._mouse_enter = None
        return val

    @event_handler
    async def on_element_leave(self, element): # pylint: disable=unused-variable
        val = False
        if self._element_enter:
            val = await self._element_enter.element.dispatch_async('on_element_leave', element)
            self._element_enter = None
        return val

    @event_handler
    async def on_mouse_drag(self, x, y, dx, dy, buttons): # pylint: disable=unused-variable
        self._mouse_pos = (x, y)
        return await self._dispatch_sub(self._mouse_press, 'on_mouse_drag', x, y, dx, dy, buttons)

    @event_handler
    async def on_mouse_press(self, x, y, button, mods, first): # pylint: disable=unused-variable
        self._mouse_pos = (x, y)
        if self._mouse_press:
            await self._dispatch_sub(self._mouse_press, 'on_mouse_press', x, y, button, mods, first=False)
            return True
        elif self._mouse_target and first:
            self._mouse_press = await self._try_dispatch('on_mouse_press', x, y, button, mods, first=True)
            if self._mouse_press:
                if self._mouse_press is not self._mouse_enter:
                    await self._mouse_enter.element.dispatch_async('on_mouse_leave')
                    self._mouse_enter = None
                return True

        return False

    @event_handler
    async def on_mouse_release(self, x, y, button, mods, last): # pylint: disable=unused-variable
        self._mouse_pos = (x, y)
        if not self._mouse_press:
            return False

        await self._dispatch_sub(self._mouse_press, 'on_mouse_release', x, y, button, mods, last=last)

        if last:
            self._mouse_press = None
            found = False
            for sub, pos in self.elements_at(x, y, actual_loc=True):
                if not found:
                    self._mouse_target = sub
                    found = True
                if self._mouse_enter is sub:
                    return True
                elif await sub.element.dispatch_async('on_mouse_enter'):
                    if self._mouse_enter:
                        await self._mouse_enter.element.dispatch_async('on_mouse_leave')
                    self._mouse_enter = sub
                    return True
            
            if self._mouse_enter:
                await self._mouse_enter.element.dispatch_async('on_mouse_leave')
                self._mouse_enter = None

            if not found:
                self._mouse_target = None

        return True

    @event_handler
    async def on_element_dropped(self, x, y, element):
        if self._element_target:
            self._element_target = None
            self._element_enter = None
            return await self._try_dispatch('on_element_dropped', x, y, element)

        return False

    @event_handler
    async def on_element_undropped(self, x, y, element):
        if self._element_target:
            self._element_target = None
            self._element_enter = None
            return await self._try_dispatch('on_element_undropped', x, y, element)

        return False

    @event_handler
    async def on_mouse_scroll(self, x, y, dx, dy): # pylint: disable=unused-variable
        self._mouse_pos = (x, y)
        if self._mouse_press:
            await self._dispatch_sub(self._mouse_press, 'on_mouse_scroll', x, y, dx, dy)
            return True
        if self._mouse_target and await self._try_dispatch('on_mouse_scroll', x, y, dx, dy):
            return True
        
        return False

    @event_handler
    async def on_key_press(self, key, mod): # pylint: disable=unused-variable
        if self._mouse_press:
            await self._dispatch_sub(self._mouse_press, 'on_key_press', key, mod)
            return True
        if self._mouse_pos and await self._try_dispatch('on_key_press', *self._mouse_pos, key, mod, _forward_pos=False):
            return True
        
        return False

    @event_handler
    async def on_key_release(self, key, mod): # pylint: disable=unused-variable
        if self._mouse_press:
            await self._dispatch_sub(self._mouse_press, 'on_key_release', key, mod)
            return True
        if self._mouse_pos and await self._try_dispatch('on_key_release', *self._mouse_pos, key, mod, _forward_pos=False):
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

    async def _dispatch_sub(self, sub: Optional[Subelement], event, x, y, *args, **kwargs):
        if sub:
            return await sub.element.dispatch_async(event, x + self._loc[0] - sub.offset[0], y + self._loc[1] - sub.offset[1], *args, **kwargs)
        else:
            return False

    async def _try_dispatch(self, event, x, y, *args, _dispatch_after=None, _tries=None, _forward_pos=True, **kwargs):
        tries = range(_tries) if _tries else itertools.count()
        for (sub, pos), _ in zip(self.elements_at(x, y, actual_loc=True, after=_dispatch_after), tries):
            if (await (sub.element.dispatch_async(event, *pos, *args, **kwargs) if _forward_pos else sub.element.dispatch_async(event, *args, **kwargs))):
                return sub

        return None

    def _on_child_position_changed(self, dx, dy, child):
        match = next(sub for sub in self._sub if sub.element is child)
        n_off = match.offset
        match.offset = (n_off[0] + dx, n_off[1] + dy)
        return True

    async def _on_child_this_dropped(self, this):
        match = next((sub for sub in self._sub if sub.element is this), None)
        if match:
            n_off = match.offset
            sz = this.size
            child_pos = (n_off[0] + (sz[0]/2), n_off[1] + (sz[1]/2))
            try:
                sub = await self._try_dispatch('on_element_dropped', *child_pos, this, _dispatch_after=this)
            except DropNotSupportedError as e:
                if self._element_enter and e.element is not self._element_enter:
                    await self._element_enter.element.dispatch_async('on_element_leave', this)
                self._element_enter = None
                await this.dispatch_async('on_drop_unsupported', e.element)
                return True
            
            if not sub:
                return False
            if sub is not self._element_enter:
                if self._element_enter:
                    await self._element_enter.element.dispatch_async('on_element_leave', this)
            self._element_enter = None
                
        return True

    async def _on_child_this_undropped(self, this):
        if self._element_enter:
            await self._element_enter.element.dispatch_async('on_element_leave', this)
        self._element_enter = None
        return True

    async def _on_child_this_dragged(self, this):
        match = next((sub for sub in self._sub if sub.element is this), None)
        if match:
            n_off = match.offset
            sz = this.size
            child_pos = (n_off[0] + (sz[0]/2), n_off[1] + (sz[1]/2))
            for sub, pos in self.elements_at(*child_pos, actual_loc=True, after=this):
                if sub is self._element_enter:
                    await self._dispatch_sub(sub, 'on_element_motion', *child_pos, this)
                    break
                elif await sub.element.dispatch_async('on_element_enter', this):
                    if self._element_enter:
                        await self._element_enter.element.dispatch_async('on_element_leave', this)
                    self._element_enter = sub
                    break
            else:
                if self._element_enter:
                    await self._element_enter.element.dispatch_async('on_element_leave', this)
                self._element_enter = None

        return True

    def _on_child_this_request_top(self, this, all=False):
        self.move_child_top(this)
        if all:
            self.dispatch('on_this_request_top', self, all)

    def _on_child_this_request_bottom(self, this, all=False):
        self.move_child_bottom(this)
        if all:
            self.dispatch('on_this_request_bottom', self, all)

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
        handle = Subelement(child, position)
        self._sub.insert(index, handle)
        return handle

    def add_child_top(self, child: ElementABC, position):
        """
        add a child element on top

        note: adding the same element which its position may change might result in an unexpected behavior
        """
        self._add_listeners(child)
        handle = Subelement(child, position)
        self._sub.append(handle)
        return handle

    def pop_child_top_sub(self) -> Subelement:
        sub = self._sub.pop()
        self._remove_listeners(sub.element)
        return sub

    def pop_child_top(self) -> ElementABC:
        return self.pop_child_top_sub().element

    def pop_child_if_sub(self, predicate: Callable[[ElementABC], bool]) -> List[Subelement]:
        _idx = {i for i, sub in enumerate(self._sub) if predicate(sub.element)}
        childs = [sub for i, sub in enumerate(self._sub) if i in _idx]
        self._sub = [sub for i, sub in enumerate(self._sub) if i not in _idx]
        for child in childs:
            self._remove_listeners(child.element)
        return childs

    def pop_child_if(self, predicate: Callable[[ElementABC], bool]) -> List[ElementABC]:
        return (sub.element for sub in self.pop_child_if_sub(predicate))

    def remove_child(self, child: Union[int, ElementABC, Subelement]):
        if isinstance(child, Subelement):
            self._sub.remove(child)
        elif isinstance(child, int):
            child = self._sub.pop(child)
        else:
            assert isinstance(child, ElementABC), 'unrecognized grid.remove_child child argument type'
            self.pop_child_if(lambda c: c is child)
            return
        
        self._remove_listeners(child.element)

    def clear(self):
        self._sub.clear()

    def move_child_top(self, child: Union[int, ElementABC, Subelement]):
        if isinstance(child, Subelement):
            child = self._sub.index(child)

        if isinstance(child, int):
            self._sub.append(self._sub.pop(child))
        else:
            assert isinstance(child, ElementABC), 'unrecognized grid.move_child_top child argument type'
            _idx = {i for i, sub in enumerate(self._sub) if sub.element is child}
            self._sub = [*(sub for i, sub in enumerate(self._sub) if i not in _idx), *(sub for i, sub in enumerate(self._sub) if i in _idx)]

    def move_child_bottom(self, child: Union[int, ElementABC, Subelement]):
        if isinstance(child, Subelement):
            child = self._sub.index(child)

        if isinstance(child, int):
            self._sub.insert(0, self._sub.pop(child))
        else:
            assert isinstance(child, ElementABC), 'unrecognized grid.move_child_top child argument type'
            _idx = {i for i, sub in enumerate(self._sub) if sub.element is child}
            self._sub = [*(sub for i, sub in enumerate(self._sub) if i in _idx), *(sub for i, sub in enumerate(self._sub) if i not in _idx)]

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


class StaticGridError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class StaticGrid(Grid):
    def __init__(self, size):
        super().__init__(size)
        self._static = True
        self._rendered = False
        self._texture = None

    def _check_rendered(self):
        if self._rendered:
            raise StaticGridError("grid is already rendered, cannot be modified")

    def _check_child_static(self, child: ElementABC):
        if not child.static:
            raise StaticGridError("static grid requires its children to be static elements")

    def _on_child_position_changed(self, dx, dy, child):
        return False

    def add_child(self, index, child: ElementABC, position):
        """
        add a child element

        note: adding the same element which its position may change might result in an unexpected behavior
        """
        self._check_rendered()
        self._check_child_static(child)
        return super().add_child(index, child, position)


    def add_child_top(self, child: ElementABC, position):
        """
        add a child element on top

        note: adding the same element which its position may change might result in an unexpected behavior
        """
        self._check_rendered()
        self._check_child_static(child)
        return super().add_child_top(child, position)

    def remove_child(self, child: Union[int, ElementABC, Subelement]):
        self._check_rendered()
        return super().remove_child(child)        

    def pop_child_top_sub(self):
        self._check_rendered()
        return super().pop_child_top_sub()

    def pop_child_if_sub(self, predicate):
        self._check_rendered()
        return super().pop_child_if_sub(predicate)

    def clear(self):
        self._check_rendered()
        return super().clear()

    def texture(self, size=None):
        if not self._rendered:
            self._rendered = True
            _back = _current_backend()
            _renderer = _back.current_renderer()
            self._texture = _back.Texture.create(_renderer, size if size else self.size, _back.TextureAccessEnum.Target)
            with _renderer.target(self._texture):
                super().render((0, 0), size=size)
                
        return self._texture

    def render(self, location, size=None):
        self.texture().draw(location, size=size)

class AlignMode(Enum):
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()

class StructuredMixin(mixin_with_typehint(Grid)):
    _line: List[ElementABC]

    def __init__(self, *args, x_off=0, y_off=0, x_dist=8, y_dist=8, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._align = AlignMode.LEFT
        self._x_off = x_off
        self._y_off = y_off
        self._x_dist = x_dist
        self._y_dist = y_dist
        self._x = x_off
        self._y = y_off
        self._high_y = 0
        self._line = list()
        self._in_line = False

    @property
    def align_mode(self):
        return self._align

    @align_mode.setter
    def align_mode(self, mode):
        self._align = mode

    @property
    def insert_location(self):
        """
        return rough location where element will be inserted next
        if called after new line is just inserted then x represents last line's x
        """
        return (self._x, self._y)

    def clear(self) -> None:
        try:
            super().clear()
        except Exception:
            raise
        self._x = self._x_off
        self._y = self._y_off
        self._high_y = 0
        self._line = list()
        self._in_line = False

    def commit(self, newline=True):
        szs = [e.size for e in self._line]
        if not self._in_line:
            self._in_line = True
            if self.align_mode == AlignMode.LEFT:
                self._x = self._x_off
            else:
                h_sz = sum(sz[0] for sz in szs) + (len(self._line)-1)*self._x_dist
                if self.align_mode == AlignMode.CENTER:
                    self._x = (self.size[0]-h_sz)/2
                else: # self.align_mode == AlignMode.RIGHT
                    self._x = self.size[0]-h_sz-self._x_off
            
        self._high_y = max(self._high_y, max(sz[1] for sz in szs))

        for sz, e in zip(szs, self._line):
            super().add_child_top(e, (self._x, self._y))
            self._x += sz[0] + self._x_dist

        self._line.clear()
        
        if newline:
            self._y += self._high_y + self._y_dist
            self._high_y = 0
            self._in_line = False

    def add_child_structured(self, *elements: ElementABC, commit=True, newline=True):
        self._line.extend(elements)
        if commit:
            self.commit(newline=newline)
        if (not commit) and newline:
            raise ValueError('newline requires committing')

    def current_line_height(self):
        return max(self._high_y, max(e.size[0] for e in self._line))
        

class StructuredGrid(StructuredMixin, Grid):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class StructuredStaticGrid(StructuredMixin, StaticGrid):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
