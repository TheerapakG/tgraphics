from abc import abstractmethod

from ....core.elementABC import ElementABC

class _FilterBase(ElementABC):
    def __init__(self, target: ElementABC, *args):
        super().__init__()
        self._target = target
        if target.static:
            self._tex = self.texture
        else:
            self._tex = None
        self.target = self._target

        self._static = target.static

        self.args = args

    @property
    def size(self):
        return self._target.size

    def render(self, location, size=None):
        if self._tex:
            self._tex.draw(location, size)
        else:
            self.texture.draw(location, size)
