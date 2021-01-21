"""
pygame (or SDL2 that is under it to be more exact) backend for tgraphics
"""

from .pygame import *
from . import mouse
from . import shapes
from . import text
from .key import Keys

__all__ = [s for s in dir() if not s.startswith('_')]
