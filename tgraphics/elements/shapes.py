from ..core.backend_loader import _current_backend
from ..core.elementABC import ElementABC

class _ShapeReflectorMixin:
    def __init__(self, cls, *args, **kwargs):
        super().__init__()
        self._instance = cls(*args, **kwargs)
        self._static = True

    @property
    def color(self):
        return self._instance.color

    def __getattr__(self, name):
        try:
            return getattr(self._instance, name)
        except AttributeError:
            pass
        
        return getattr(super(), name)


class Point(_ShapeReflectorMixin, ElementABC):
    def __init__(self, color=(255, 255, 255, 255)):
        super().__init__(_current_backend().shapes.Point, color)

    @property
    def size(self):
        return 1, 1

    def render(self, location, size=None):
        self._instance.draw(location)


class Line(_ShapeReflectorMixin, ElementABC):
    def __init__(self, vec, color=(255, 255, 255, 255)):
        super().__init__(_current_backend().shapes.Line, color)
        self._vec = vec

    @property
    def size(self):
        return (abs(i) for i in self._vec)

    def render(self, location, size=None):
        if size:
            vec = (i/abs(i)*j for i, j in zip(self._vec, size))
        else:
            vec = self._vec
        self._instance.draw(location, vec)


class Rectangle(_ShapeReflectorMixin, ElementABC):
    def __init__(self, size, color=(255, 255, 255, 255)):
        super().__init__(_current_backend().shapes.Rectangle, color)
        self._size = size

    @property
    def size(self):
        return self._size

    def render(self, location, size=None):
        self._instance.draw(location, size if size else self._size)


__all__ = [s for s in dir() if not s.startswith('_')]
