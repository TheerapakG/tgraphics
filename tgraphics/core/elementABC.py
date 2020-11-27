from abc import ABC, abstractmethod
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

    def dispatch_event(self, event):
        return False
