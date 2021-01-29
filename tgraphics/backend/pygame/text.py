from functools import lru_cache
from io import FileIO
from operator import itemgetter
from pygame.freetype import Font, SysFont
from string import printable
from typing import Optional, Union

from .pygame import current_renderer, Surface, Texture

MAX_LINEAR_SCALEUP = 1.5

INITIAL_FONT_PT = 50

DEFAULT_FONT = None
def set_default_font(font):
    global DEFAULT_FONT
    if not font:
        DEFAULT_FONT = None
    else:
        DEFAULT_FONT = Font(font, 0)

@lru_cache(maxsize=128)
def _get_font(font, bold, italic) -> Font:
    if not font:
        if DEFAULT_FONT:
            font = DEFAULT_FONT
        else:
            font = SysFont('', 0, bold, italic)
    elif isinstance(font, str):
        font = SysFont(font, 0, bold, italic)
    else:
        font = Font(font, 0, 4)
    return font

@lru_cache(maxsize=128)
def _get_font_ascii_ascend_descend(font):
    """
    font metrics are sometimes for just ASCII, sometimes are for all
    code point exists in the font, here we figure out metrics for just ASCII
    """
    metrics = [m for m in font.get_metrics(printable, size=INITIAL_FONT_PT) if m]
    return (max(metrics, key=itemgetter(3))[3]/INITIAL_FONT_PT, min(metrics, key=itemgetter(2))[2]/INITIAL_FONT_PT)

class Label:
    def __init__(self, text: str, font: Optional[Union[str, FileIO]], bold: bool, italic, size: int, color=(255, 255, 255, 255)):
        """
        a class to facilitate drawing short texts (often within a line)
        
        parameters:
            text: str
                the text
            font_name: str
                the name of the font that will be used to render the text
            bold: bool
                whether the text is bolded or not
            italic: bool
                whether the text is italicized or not
            size: int
                the final text size (height) in pixels
            [color]
                the color of the text, default to white at maximum opacity
        """
        self._text = text
        self._font = _get_font(font, bold, italic)
        self._col = color

        self._texttext = dict()
        self._gen_surface(size)
        self._size = self._c_size

    def _gen_surface(self, height):
        ascend, descend = _get_font_ascii_ascend_descend(self._font)
        factor = 1/(ascend-descend)
        metrics = self._font.get_metrics(self._text, size=height*factor)
        self._c_off = height*ascend - max(metrics, key=itemgetter(3))[3]

        _surf, _bound = self._font.render(self._text, fgcolor=self._col, size=height*factor)
        self._textsurface = Surface(_surf)
        self._c_size = (self._textsurface.w, height)

    @property
    def size(self):
        return self._size
    
    def draw(self, position, height = None):
        if height and self._c_size[1] * MAX_LINEAR_SCALEUP < height:
            self._gen_surface(height)

        rdr = current_renderer()
        if rdr not in self._texttext or (height and self._texttext[rdr][1][1] * MAX_LINEAR_SCALEUP < height):
            self._texttext[rdr] = (Texture.from_surface(rdr, self._textsurface), self._c_off, self._c_size[1])

        height = height if height else self._size[1]
        textinfo = self._texttext[rdr]
        texture = textinfo[0]
        factor = (height / textinfo[2])

        position = (position[0], position[1] + textinfo[1]*factor)
        bottom = (texture.w*factor, texture.h*factor)

        texture.blit_to_target(dst_rect_or_coord=(*position, *bottom))
