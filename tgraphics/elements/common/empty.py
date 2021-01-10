from ...core.elementABC import ElementABC

class Empty(ElementABC):
    def __init__(self, size=(0, 0)):
        """
        Element that does nothing, useful for sensing events
        """
        super().__init__()
        self._size = size
        self._static = True
        
    @property
    def size(self):
        return self._size

    def render(self, location, size=None):
        pass
