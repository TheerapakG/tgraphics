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
        _back = _current_backend()
        _rdr = orig_tex.renderer
        _tex = _back.Texture.create_as_target(_rdr, size if size else self.size, blend=orig_tex.blend_mode)
        with _rdr.target(_tex):
            orig_tex.draw((0, 0))
            _current_backend().shapes.Rectangle((0, 0, 0, int(255*self.args[0]))).draw((0, 0), size if size else self.size)
        return _tex


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
