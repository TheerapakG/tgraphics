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
        """
        static implies element will give same render result for same size
        """
        return self._static

    def texture(self, size=None):
        _back = _current_backend()
        _rdr = _back.current_renderer()
        _tex = _back.Texture.create_as_target(_rdr, size if size else self.size, blend=_current_backend().BlendMode.BLENDMODE_BLEND)
        with _rdr.target(_tex):
            self.render((0, 0), size)
        return _tex
