from enum import auto, Enum

from ...core.elementABC import ElementABC
from ..shapes import Rectangle

class ButtonType(Enum):
    DEFAULT = auto()
    TOGGLE = auto()
    DISABLE = auto()

class ButtonState(Enum):
    OFF = auto()
    HOVER = auto()
    ON = auto()
    DISABLED = auto()

class Button(ElementABC):
    _type: ButtonType
    _state: ButtonState

    def __init__(self, size, fg, **kwargs):
        super().__init__()
        self._sz = size
        self._type = kwargs.get('type', ButtonType.DEFAULT)
        self._state = ButtonState.OFF if self._type != ButtonType.DISABLE else ButtonState.DISABLED

        bg = kwargs.get('bg', None)
        self._normal = (fg, None) if not bg else (fg, bg)

        _h_fg = kwargs.get('hover_fg', fg)
        _h_bg = kwargs.get('hover_bg', bg if bg else Rectangle(size, (0, 0, 0, 31)))
        self._hover = (_h_fg, _h_bg)(15/16, 1) if _h_fg is not fg and (bg and _h_bg is not bg) else (_h_fg, _h_bg)
        
        _c_fg = kwargs.get('clicked_fg', fg)
        _c_bg = kwargs.get('clicked_bg', bg if bg else Rectangle(size, (0, 0, 0, 127)))
        self._clicked = (_c_fg, _c_bg)(3/4, 1) if _c_fg is not fg and (bg and _c_bg is not bg) else (_c_fg, _c_bg)

        _d_fg = kwargs.get('disabled_fg', fg)
        _d_bg = kwargs.get('disabled_bg', bg)
        self._disabled = (_d_fg, _d_bg)('grayscale'(1), 1/4) if _d_fg is not fg and _d_bg is not bg else (_d_fg, _d_bg)

    @property
    def size(self):
        return self._sz

    @size.setter
    def size(self, size):
        self._sz = size

    @property
    def type(self):
        return self._type

    @type.setter
    def size(self, type):
        self._type = type

    def render(self, location, size=None):
        pass
