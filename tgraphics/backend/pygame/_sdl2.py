# module for exposing sdl2 functions

import ctypes
import os
from pathlib import Path
import pygame
import sys

_pygame_dir = Path(pygame.__file__).parent

if sys.platform == 'win32':
    _sdl2_dir = _pygame_dir
    _sdl2_name = 'sdl2'
else:
    _sdl2_dir = _pygame_dir.parent / 'pygame.libs'
    # fron testing, ctypes.util.find_library IS useless (which is expected since we probably need to do ldconfig stuff)
    # name will probably be either libSDL2-{}.so.{} or libSDL2-{}.dylib
    for name in os.listdir(_sdl2_dir):
        if 'libSDL2-' in name:
            _sdl2_name = name

_cwd = os.getcwd()
os.chdir(_sdl2_dir)

_sdl2 = ctypes.CDLL(_sdl2_name)

def sdl_capturemouse(enabled):
    _sdl2.SDL_CaptureMouse(ctypes.c_bool(enabled))

os.chdir(_cwd)
