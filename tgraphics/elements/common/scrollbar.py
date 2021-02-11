from .button import Button
from .grid import Grid
from .mixin.dragablemixin import DragableMixin
from ..shapes import Rectangle

class _Bar(DragableMixin, Button):
    def __init__(self, size, movement_func, **kwargs):
        kwargs['drag_transform'] = movement_func
        kwargs.setdefault('fg', None)
        kwargs.setdefault('bg', Rectangle(size, color=(127, 127, 127, 63)))
        kwargs.setdefault('hover_bg', Rectangle(size, color=(127, 127, 127, 95)))
        super().__init__(size, **kwargs)


class HorizontalScrollbar(Grid):
    def __init__(self, size, content_width, **kwargs):
        self._content_width = content_width
        super().__init__(size)
        self._bar = _Bar((self._bar_length(), self.size[1]), self._bar_movement_calc, **kwargs)
        self.add_child_top(self._bar, (0, 0))
        self._bar.event['on_this_dragged'].add_listener(lambda this: self.dispatch('on_scroll', self.represented_section))

    def _bar_length(self):
        _size_x = self.size[0]
        return min((_size_x*_size_x)/self._content_width, _size_x)

    def _bar_movement_calc(self, mousex, mousey, dx, dy):
        _size_x = self.size[0]
        _travel_x = _size_x - self._bar_length()
        if mousex < 0:
            return (0, 0)
        if mousex > _travel_x:
            return (_travel_x, 0)
        return (mousex, 0)

    @property
    def content_width(self):
        return self._content_width

    @content_width.setter
    def content_width(self, w):
        self._content_width = w
        self._bar.size = (self._bar_length(), self.size[1])

    @property
    def represented_section(self):
        _size_x = self.size[0]
        bar_left = self._bar.pos[0]
        return ((bar_left * self._content_width)/_size_x, ((bar_left + self._bar_length()) * self._content_width)/_size_x)


class VerticalScrollbar(Grid):
    def __init__(self, size, content_height, **kwargs):
        self._content_height = content_height
        super().__init__(size)
        self._bar = _Bar((self.size[0], self._bar_height()), self._bar_movement_calc, **kwargs)
        self.add_child_top(self._bar, (0, 0))
        self._bar.event['on_this_dragged'].add_listener(lambda this: self.dispatch('on_scroll', self.represented_section))

    def _bar_height(self):
        _size_y = self.size[1]
        return min((_size_y*_size_y)/self._content_height, _size_y)

    def _bar_movement_calc(self, mousex, mousey, dx, dy):
        _size_y = self.size[1]
        _travel_y = _size_y - self._bar_height()
        if mousey < 0:
            return (0, 0)
        if mousey > _travel_y:
            return (0, _travel_y)
        return (0, mousey)

    @property
    def content_height(self):
        return self._content_height

    @content_height.setter
    def content_height(self, h):
        self._content_height = h
        self._bar.size = (self.size[0], self._bar_height())

    @property
    def represented_section(self):
        _size_y = self.size[1]
        bar_left = self._bar.pos[1]
        return ((bar_left * self._content_height)/_size_y, ((bar_left + self._bar_height()) * self._content_height)/_size_y)
