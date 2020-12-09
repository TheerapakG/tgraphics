from abc import ABC, abstractmethod

from ..core.backend_loader import _current_backend
from ._eventdispatch import EventDispatcher

class ElementABC(EventDispatcher, ABC):
    def __init__(self):
        super().__init__()
        self._static = False
        
    @property
    @abstractmethod
    def size(self):
        raise NotImplementedError()

    @abstractmethod
    def render(self, location, size=None):
        raise NotImplementedError()

    @property
    def static(self):
        return self._static

    @property
    def texture(self):
        _back = _current_backend()
        _rdr = _back._current_renderer()
        _tex = _back.Texture.create_as_target(_rdr, self.size, transparent=True)
        with _rdr.target(_tex):
            self.render((0, 0))
        return _tex
