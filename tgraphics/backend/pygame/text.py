from functools import lru_cache

import pygame
from pygame.freetype import Font, SysFont

from .pygame import _current_renderer, Surface, Texture

MAX_LINEAR_SCALEUP = 1.5

INITIAL_FONT_PT = 20

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
        self._size = size
        self._col = color
        self._factor = None

        self._texttext = dict()
        self._gen_surface(self._size)

    def _gen_surface(self, height):
        if not self._factor:
            _surf, _bound = self._font.render(self._text, fgcolor=self._col, size=INITIAL_FONT_PT)
            self._textsurface = Surface(_surf)
            self._factor = INITIAL_FONT_PT/self._textsurface.h
            if self._textsurface.h >= self._size:
                return
        
        _surf, _bound = self._font.render(self._text, fgcolor=self._col, size=height*self._factor)
        self._textsurface = Surface(_surf)

    @property
    def size(self):
        return self._size / self._textsurface.h * self._textsurface.w, self._size
    
    def draw(self, position, height = None):
        if height and self._textsurface.h * MAX_LINEAR_SCALEUP < height:
            self._gen_surface(height)

        rdr = _current_renderer()
        if rdr not in self._texttext or (height and self._texttext[rdr].h * MAX_LINEAR_SCALEUP < height):
            self._texttext[rdr] = Texture.from_surface(rdr, self._textsurface)

        if height:
            bottom = (height / position[1] * position[0]) + position[0], height + position[1]
        else:
            _sz = self.size
            bottom = _sz[0] + position[0], _sz[1] + position[1]

        self._texttext[rdr].blit_to_target(dst_rect_or_coord=(*position, *bottom))
