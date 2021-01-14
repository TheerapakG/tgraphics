from ....core.backend_loader import _current_backend
from ....core.elementABC import DropNotSupportedError, ElementABC

class DragableMixin(ElementABC):
    def __init__(self, *args, drag_transform = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._pos = (0, 0)
        self._start_pos = None
        self._l_pos = None
        self._transform_f = drag_transform

        e_h = self.event['on_mouse_press'].handler
        self._on_mouse_press = e_h if e_h is not None else lambda *args, **kwargs: True

        @self.event
        def on_mouse_press(x, y, button, mods, first): 
            res = self._on_mouse_press(x, y, button, mods, first=first)
            if first and button == _current_backend().mouse.LEFT:
                self._start_pos = self._pos
                self._l_pos = self._pos
                self.dispatch('on_this_start_dragged', this=self)
                self.dispatch('on_this_dragged', this=self)
                return True
            if not first and button != _current_backend().mouse.LEFT:
                self._start_pos = None
                self._l_pos = None
                self.dispatch('on_this_undropped', this=self)
                return True
            return res

        e_h = self.event['on_mouse_drag'].handler
        self._on_mouse_drag = e_h if e_h is not None else lambda *args, **kwargs: True

        @self.event
        def on_mouse_drag(x, y, dx, dy, buttons): 
            res = self._on_mouse_drag(x, y, dx, dy, buttons)
            if self._l_pos:
                self._l_pos = (self._l_pos[0] + dx, self._l_pos[1] + dy)
                _n_pos = self._transform_f(*self._l_pos) if self._transform_f else self._l_pos
                self.pos = _n_pos
                self.dispatch('on_this_dragged', this=self)
                return True
            return res

        e_h = self.event['on_mouse_release'].handler
        self._on_mouse_release = e_h if e_h is not None else lambda *args, **kwargs: True

        @self.event
        def on_mouse_release(x, y, button, mods, last): 
            res = self._on_mouse_release(x, y, button, mods, last=last)
            mouse = _current_backend().mouse
            if button == mouse.LEFT and self._l_pos:
                try:
                    if not self.dispatch('on_this_dropped', this=self):
                        self.dispatch('on_drop_on_empty')
                except DropNotSupportedError as e:
                    self.dispatch('on_drop_unsupported', e.element)
                self._start_pos = None
                self._l_pos = None
                return True
            return res

        def _on_position_changed(_dx, _dy, _):
            pos = self._pos
            self._pos = (pos[0] + _dx, pos[1] + _dy)

        self.event['on_position_changed'].add_listener(_on_position_changed)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        if self._pos != value:
            dx, dy = value[0] - self._pos[0], value[1] - self._pos[1]
            self.dispatch('on_position_changed', dx, dy, self)

    @property
    def start_pos(self):
        return self._start_pos
