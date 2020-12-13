from ....core.elementABC import ElementABC

class DragableMixin(ElementABC):
    def __init__(self, *args, drag_transform = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._pos = (0, 0)
        self._transform_f = drag_transform

        @self.event
        def on_mouse_drag(self, x, y, dx, dy, buttons): 
            _n_pos = (self._pos[0] + dx, self._pos[1] + dy)
            if self._transform_f:
                _n_pos = self._transform_f(*_n_pos)

            self.pos = _n_pos

        @property
        def pos(self):
            return self._pos

        @pos.setter
        def pos(self, value):
            if self._pos != value:
                self._pos = value
                self.dispatch('on_position_changed', *self._pos)
