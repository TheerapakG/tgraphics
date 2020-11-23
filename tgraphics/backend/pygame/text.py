from functools import lru_cache

import pygame
from pygame.freetype import Font, SysFont

from .pygame import _current_renderer, Surface, Texture

MAX_LINEAR_SCALEUP = 1.5
# assume 96 PPI like CSS
PX_TO_PT = 0.75
OVERSIZE_FACTOR = 2.5

@lru_cache(maxsize=128)
def _get_font(font_name, bold, italic):
    font = SysFont(font_name, 0, bold, italic)
    return font

class Label:
    def __init__(self, text, font_name, bold, italic, size_px, color=(255, 255, 255, 255)):
        self._text = text
        self._font_name = font_name
        self._b = bold
        self._i = italic
        self._size = size_px
        self._col = color

        _surf, _bound = _get_font(font_name, bold, italic).render(text, fgcolor=color, size = self._size * PX_TO_PT * OVERSIZE_FACTOR)
        self._textsurface = Surface(_surf)
        self._texttext = dict()

    @property
    def size(self):
        return self._size / self._textsurface.h * self._textsurface.w, self._size
    
    def draw(self, position, height = None):
        if height and self._textsurface.h * OVERSIZE_FACTOR * MAX_LINEAR_SCALEUP < height:
            _surf, _bound = _get_font(self._font_name, self._b, self._i).render(self._text, fgcolor=self._col, size=height * PX_TO_PT * OVERSIZE_FACTOR)
            self._textsurface = Surface(_surf)

        rdr = _current_renderer()
        if rdr not in self._texttext or (height and self._texttext[rdr].h * OVERSIZE_FACTOR * MAX_LINEAR_SCALEUP < height):
            self._texttext[rdr] = Texture.from_surface(rdr, self._textsurface)

        if height:
            bottom = (height / position[1] * position[0]) + position[0], height + position[1]
        else:
            _sz = self.size
            bottom = _sz[0] + position[0], _sz[1] + position[1]
        self._texttext[rdr].blit_to_target(dst_rect_or_coord=(*position, *bottom))
