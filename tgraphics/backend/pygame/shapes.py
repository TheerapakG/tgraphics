import pygame

from .pygame import current_renderer

class BasicShapeProperties:
    def __init__(self, color=(255, 255, 255, 255)):
        self._col = color

    @property
    def color(self):
        return self._col

    @color.setter
    def color(self, value):
        self._col = value


class Point(BasicShapeProperties):
    def draw(self, point):
        rdr = current_renderer()
        with rdr.draw_color(self._col):
            rdr.draw_point(point)


class Line(BasicShapeProperties):
    def draw(self, point, point2):
        rdr = current_renderer()
        with rdr.draw_color(self._col):
            rdr.draw_line(point, point2)


class Rectangle(BasicShapeProperties):
    def draw(self, point, size):
        rdr = current_renderer()
        with rdr.draw_color(self._col):
            rdr.fill_rect((*point, *size))
