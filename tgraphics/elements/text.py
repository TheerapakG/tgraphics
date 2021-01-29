from ..core.backend_loader import _current_backend
from ..core.elementABC import ElementABC

def set_default_font(font):
    _current_backend().text.set_default_font(font)

class Label(ElementABC):
    def __init__(self, text, size, *, font='', bold=False, italic=False, color=(255, 255, 255, 255)):
        super().__init__()
        self._instance = _current_backend().text.Label(text, font, bold, italic, size, color)
        self._static = True

    @property
    def size(self):
        return self._instance.size
    
    def render(self, location, size=None):
        if size:
            _sz = self.size
            factor = min(size[0]/_sz[0], size[1]/_sz[1])
            _actual = (factor * _sz[0], factor * _sz[1])
            _loc = ((size[0] - _actual[0])/2 + location[0], (size[1] - _actual[1])/2 + location[1])
            height = _actual[1]
        else:
            _loc, height = location, None

        self._instance.draw(_loc, height)
