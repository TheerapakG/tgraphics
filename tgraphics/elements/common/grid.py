from typing import List, Tuple
from pygame import Rect

from ...core.backend_loader import _current_backend
from ...core.elementABC import ElementABC

class Grid(ElementABC):
    _sub: List[Tuple[ElementABC, Tuple[int, int]]]

    def __init__(self):
        super().__init__()
        self._sub = list()

    def add_child(self, index, child: ElementABC, position):
        self._sub.insert(index, (child, position))

    def add_child_top(self, child: ElementABC, position):
        self._sub.append((child, position))

    def remove_child(self, child):
        raise NotImplementedError()

    def remove_child_top(self):
        self._sub.pop()

    def _bound(self):
        all_loc = [Rect(pos, c.size) for c, pos in self._sub]
        return Rect.union(all_loc)

    @property
    def bound(self):
        _b = self._bound()
        return (_b.topleft, _b.bottomright)

    @property
    def size(self):
        return self._bound().size

    def render(self, location, size=None):
        for c, pos in self._sub:
            _sz = c.size
            x, y = location[0] + pos[0], location[1] + pos[1]
            if x + _sz[0] >= 0 and y + _sz[1] >= 0:
                if size:
                    if x > size[0] and y > size[1]:
                        continue
                c.render((x, y))
