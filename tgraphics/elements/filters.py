from .filterABC import FilterABC
from ..core.backend_loader import _current_backend

class Brightness(FilterABC):
    """
    Show element at lower brightness
    
    parameters:
        target
            the element
        args[0]
            brightness (0.0-1.0)
    """
    def texture(self, size=None):
        orig_tex = self._target.texture(size)
        return orig_tex.as_color_mod((int(255*self.args[0]), int(255*self.args[0]), int(255*self.args[0]), 255))


class Opacity(FilterABC):
    """
    Show element at lower opacity
    
    parameters:
        target
            the element
        args[0]
            opacity (0.0-1.0)
    """
    def texture(self, size=None):
        orig_tex = self._target.texture(size)
        return orig_tex.as_color_mod((255, 255, 255, int(255*self.args[0])))


class Scale(FilterABC):
    """
    Scale element
    
    parameters:
        target
            the element
        args[0]
            size
    """
    def texture(self, size=None):
        return self._target.texture(size if size else self._sz)
