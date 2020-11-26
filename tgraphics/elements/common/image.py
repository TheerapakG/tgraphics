from ...core.backend_loader import _current_backend
from ...core.elementABC import ElementABC

class Image(ElementABC):
    def __init__(self, _texture):
        self._texture = _texture

    @staticmethod
    def from_file(filename):
        _back = _current_backend()
        return Image(_back.Texture.from_file(_back._current_renderer(), filename))

    @staticmethod
    def from_io(io, ext_hint):
        _back = _current_backend()
        return Image(_back.Texture.from_file(_back._current_renderer(), io, ext_hint))

    @property
    def size(self):
        return self._texture.size

    def render(self, location, size=None):
        self._texture.draw(location, size)
