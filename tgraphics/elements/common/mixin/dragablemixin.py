from ....core.backend_loader import _current_backend
from ....core.elementABC import ElementABC

class DragableMixin(ElementABC):
    def __init__(self, *args, drag_transform = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._pos = (0, 0)
        self._l_pos = None
        self._transform_f = drag_transform
        
        e_h = self.event['on_mouse_first_press'].handler
        self._on_mouse_first_press = e_h if e_h is not None else lambda *args, **kwargs: True

        @self.event
        def on_mouse_first_press(x, y, button, mods): 
            res = self._on_mouse_first_press(x, y, button, mods)
            if button == _current_backend().mouse.LEFT:
                self._l_pos = self._pos
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
                return True
            return res

        e_h = self.event['on_mouse_release'].handler
        self._on_mouse_release = e_h if e_h is not None else lambda *args, **kwargs: True

        @self.event
        def on_mouse_release(x, y, button, mods): 
            res = self._on_mouse_release(x, y, button, mods)
            if button == _current_backend().mouse.LEFT:
                self._l_pos = None
                return True
            return res

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        if self._pos != value:
            dx, dy = value[0] - self._pos[0], value[1] - self._pos[1]
            self._pos = value
            self.dispatch('on_position_changed', self, dx, dy)
