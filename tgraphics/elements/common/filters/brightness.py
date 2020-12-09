from ._filter_base import _FilterBase
from ....core.backend_loader import _current_backend

class Brightness(_FilterBase):
    """
    Show element at lower brightness
    
    parameters:
        target
            the element
        args[0]
            brightness (0.0-1.0)
    """
    def texture(self):
        orig_tex = self._target.texture
        dark_tex = orig_tex.as_color_mod((0, 0, 0, 255))
        _back = _current_backend()
        _rdr = _back._current_renderer()
        _tex = _back.Texture.create_as_target(_rdr, self.size, transparent=True)
        with _rdr.target(_tex):
            orig_tex.draw((0, 0))
            dark_tex.draw((0, 0))
        return _tex
