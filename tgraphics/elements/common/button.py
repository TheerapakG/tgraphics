from ...core.elementABC import ElementABC

class Button(ElementABC):
    def __init__(self, size):
        super().__init__()
        self._sz = size

    @property
    def size(self):
        return self._sz

    def render(self, location, size=None):
        pass
