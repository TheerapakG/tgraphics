from functools import lru_cache
from operator import itemgetter

import pygame
from pygame.freetype import Font, SysFont

from .pygame import current_renderer, Surface, Texture

MAX_LINEAR_SCALEUP = 1.5

INITIAL_FONT_PT = 50

@lru_cache(maxsize=128)
def _get_font(font_name, bold, italic) -> Font:
    font = SysFont(font_name, 0, bold, italic)
    return font

class Label:
    def __init__(self, text: str, font_name: str, bold: bool, italic, size: int, color=(255, 255, 255, 255)):
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
        self._font = _get_font(font_name, bold, italic)
        self._col = color

        self._texttext = dict()
        self._gen_surface(size)
        self._size = self._c_size

    def _gen_surface(self, height):
        ascender = self._font.get_sized_ascender(height)
        factor = height/(ascender - self._font.get_sized_descender(height))
        self._c_off = ascender - max(self._font.get_metrics(self._text, size=height*factor), key=itemgetter(3))[3]

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
