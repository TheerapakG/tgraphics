from enum import Flag, auto
from functools import reduce
from operator import or_
from typing import TYPE_CHECKING

class MouseButton(Flag):
    LEFT = auto()
    MIDDLE = auto()
    RIGHT = auto()

_buttons = list(MouseButton)

if TYPE_CHECKING:
    def _inc_bit():
        i = 1
        while True:
            yield i
            i <<= 1

    LEFT = _inc_bit()
    MIDDLE = _inc_bit()
    RIGHT = _inc_bit()

    del _inc_bit
else:
    for s in dir(MouseButton):
        if not s.startswith('_'):
            globals()[s] = v = getattr(MouseButton, s)

NButton = LEFT & MIDDLE

def _mouse_from_pyg(_pyg):
    return _buttons[_pyg-1]

def _mouse_from_pygtpl(tpl):
    return reduce(or_, (b for b, v in zip(_buttons, tpl) if v), NButton)
