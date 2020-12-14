from ....core.backend_loader import _current_backend
from ....core.elementABC import ElementABC

class DragableMixin(ElementABC):
    def __init__(self, *args, drag_transform = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._pos = (0, 0)
        self._l_pos = None
        self._transform_f = drag_transform

        @self.event
        def on_mouse_drag(self, x, y, dx, dy, buttons): 
            if not self._l_pos:
                self._l_pos = self._pos
            self._l_pos = (self._l_pos[0] + dx, self._l_pos[1] + dy)
            _n_pos = self._transform_f(*self._l_pos) if self._transform_f else self._l_pos
            self.pos = _n_pos

        @self.event
        def on_mouse_last_release(self, x, y, dx, dy, buttons): 
            self._l_pos = None

        @property
        def pos(self):
            return self._pos

        @pos.setter
        def pos(self, value):
            if self._pos != value:
                self._pos = value
                self.dispatch('on_position_changed', *self._pos)
