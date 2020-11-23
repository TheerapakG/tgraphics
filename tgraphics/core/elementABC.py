from abc import ABC, abstractmethod

class ElementABC(ABC):
    @property
    @abstractmethod
    def size(self):
        raise NotImplementedError()

    @abstractmethod
    def render(self, location, size=None):
        raise NotImplementedError()

    def dispatch_event(self, event):
        return False
