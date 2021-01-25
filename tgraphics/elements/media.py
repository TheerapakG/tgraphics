from ..core.backend_loader import _current_backend
from ..core.elementABC import ElementABC

class Player(ElementABC):
    def __init__(self):
        super().__init__()
        self._player = _current_backend().media.Player()

    def play(self):
        self._player.play()

    def append(self, source):
        self._player.append(source)

    @property
    def size(self):
        if self._player and self._player.source:
            return self._player.source.size
        return (0, 0)

    def render(self, location, size=None):
        texture = self._player.texture
        if texture:
            texture.draw(location, size)

    def texture(self, size=None):
        if size:
            return self._player.texture.as_size(size)
        return self._player.texture

# PEP562
def __getattr__(name: str):
    if name in globals():
        return globals()[name]
    # not implemented/cannot be abstracted in core
    return getattr(_current_backend().media, name) # pylint: disable=undefined-variable
