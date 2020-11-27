from ..core.backend_loader import _current_backend
from ..core.elementABC import ElementABC

class Label(ElementABC):
    def __init__(self, text, font_name, bold, italic, size, color=(255, 255, 255, 255)):
        super().__init__()
        self._instance = _current_backend().text.Label(text, font_name, bold, italic, size, color)

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
