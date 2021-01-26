from abc import abstractmethod

from ..core.elementABC import ElementABC

class FilterABC(ElementABC):
    def __init__(self, target: ElementABC, *args, size=None):
        super().__init__()
        self._target = target

        self._sz = size

        self._static = target.static

        self.args = args
        
        if target.static:
            self._tex = self.texture(size)
        else:
            self._tex = None
        self.target = self._target

    @property
    def size(self):
        return self._sz if self._sz else self._target.size

    @abstractmethod
    def texture(self):
        raise NotImplementedError()

    def render(self, location, size=None):
        if self._tex and not size:
            self._tex.draw(location)
        else:
            texture = self.texture(size if size else self._sz)
            if texture:
                texture.draw(location)
