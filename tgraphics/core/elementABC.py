from abc import ABC, abstractmethod

from .core import Window
from ._eventdispatch import EventDispatcher

class ElementABC(EventDispatcher, ABC):
    def __init__(self):
        super().__init__()
        
    @property
    @abstractmethod
    def size(self):
        raise NotImplementedError()

    @abstractmethod
    def render(self, location, size=None):
        raise NotImplementedError()

    def dispatch(self, event, *args, **kwargs):
        if event == 'on_mouse_press':
            ret = super().dispatch(event, *args, **kwargs)
            if ret and not Window._current_mouse_interact._mouse_target:
                Window._current_mouse_interact._mouse_target = self
            return ret
        else:
            return super().dispatch(event, *args, **kwargs)
