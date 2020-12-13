from enum import auto, Enum

from ...core.backend_loader import _current_backend
from ...core.elementABC import ElementABC
from ..shapes import Rectangle
from ..filters import Brightness, Opacity

class ButtonType(Enum):
    DEFAULT = auto()
    TOGGLE = auto()
    DISABLE = auto()

class ButtonState(Enum):
    OFF = auto()
    ON = auto()
    DISABLED = auto()

class _ButtonRenderHelper(ElementABC):
    def __init__(self, fg, bg, size):
        super().__init__()
        self.fg = fg
        self.bg = bg
        self._sz = size
        self._static = self.fg.static and (not self.bg or self.bg.static)

    @property
    def size(self):
        return self._sz

    def render(self, location, size=None):
        size = size if size else self.size 
        if self.bg:
            self.bg.render(location, None if self.bg.size==size else size)
        _fg_size = self.fg.size
        self.fg.render((location[0]+(size[0]-_fg_size[0])/2, location[1]+(size[1]-_fg_size[1])/2))


class _ButtonBGDefaultType:
    def __bool__(self):
        return False


ButtonBGDefault = _ButtonBGDefaultType()

class Button(ElementABC):
    _type: ButtonType
    _state: ButtonState
    cls_kwargs = {'button_type', 'fg', 'bg', 'hover_fg', 'hover_bg', 'clicked_fg', 'clicked_bg', 'disabled_fg', 'disabled_bg'}

    def __init__(self, size, **kwargs):
        super().__init__()
        self._sz = size
        self._type = kwargs.pop('button_type', ButtonType.DEFAULT)
        self._state = ButtonState.OFF if self._type != ButtonType.DISABLE else ButtonState.DISABLED

        fg = kwargs.pop('fg', Rectangle(size, (0, 0, 0, 31)))
        bg = kwargs.pop('bg', ButtonBGDefault)
        _bg_default = bg is ButtonBGDefault
        self._normal = _ButtonRenderHelper(fg, None, size) if not bg else _ButtonRenderHelper(fg, bg, size)

        _h_fg = kwargs.pop('hover_fg', fg)
        _h_bg = kwargs.pop('hover_bg', bg if not _bg_default else Rectangle(size, (0, 0, 0, 15)))
        self._hover = Brightness(_ButtonRenderHelper(_h_fg, _h_bg, size), 15/16) if _h_fg is fg and _h_bg is bg else _ButtonRenderHelper(_h_fg, _h_bg, size)
        
        _c_fg = kwargs.pop('clicked_fg', fg)
        _c_bg = kwargs.pop('clicked_bg', bg if not _bg_default else Rectangle(size, (0, 0, 0, 63)))
        self._clicked = Brightness(_ButtonRenderHelper(_c_fg, _c_bg, size), 3/4) if _c_fg is fg and _c_bg is bg else _ButtonRenderHelper(_c_fg, _c_bg, size)

        _d_fg = kwargs.pop('disabled_fg', fg)
        _d_bg = kwargs.pop('disabled_bg', bg)
        self._disabled = Opacity(_ButtonRenderHelper(_d_fg, _d_bg, size), 1/2) if _d_fg is fg and _d_bg is bg else _ButtonRenderHelper(_d_fg, _d_bg, size)

        self._hovering = False
        self._clicking = False

        @self.event
        def on_mouse_enter(): # pylint: disable=unused-variable
            self._hovering = True
            return True

        @self.event
        def on_mouse_leave(): # pylint: disable=unused-variable
            self._hovering = False
            return True

        @self.event
        def on_mouse_press(x, y, button, mods): # pylint: disable=unused-variable
            self._clicking = True
            return True

        @self.event
        def on_mouse_release(x, y, button, mods): # pylint: disable=unused-variable
            if _current_backend().mouse.pressed() == _current_backend().mouse.NButton:
                self._clicking = False
                if self._type == ButtonType.DISABLE:
                    return True
                if 0 > x or 0 > y or x > self._sz[0] or y > self._sz[1]:
                    self._hovering = False
                elif self._type == ButtonType.TOGGLE:
                    if self._state == ButtonState.OFF:
                        self._state = ButtonState.ON
                        self.dispatch('on_button_on')
                    else:
                        self._state = ButtonState.OFF
                        self.dispatch('on_button_off')
                else:
                    self.dispatch('on_button_press')

    @property
    def size(self):
        return self._sz

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type
        if type == ButtonType.DISABLE:
            self._state = ButtonState.DISABLED
        elif type == ButtonType.DEFAULT:
            self._state = ButtonState.OFF

    def render(self, location, size=None):
        if self._state == ButtonState.DISABLED:
            self._disabled.render(location, size)
        elif self._clicking:
            self._clicked.render(location, size)
        elif self._hovering and self._state == ButtonState.OFF:
            self._hover.render(location, size)
        elif self._state == ButtonState.OFF:
            self._normal.render(location, size)
        elif self._state == ButtonState.ON:
            self._clicked.render(location, size)
