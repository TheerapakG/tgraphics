# module for exposing sdl2 functions

import ctypes
import os
from pathlib import Path
import pygame
import sys

from .syswm import *
from .events import *

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


def SDL_VERSION(x):
    x.major, x.minor, x.patch = pygame.get_sdl_version()

_cwd = os.getcwd()
os.chdir(_sdl2_dir)

_sdl2 = ctypes.CDLL(_sdl2_name)

class SDL_Window_p(ctypes.c_void_p):
    pass

class SDL_Renderer_p(ctypes.c_void_p):
    pass


_sdl2_getrenderer = _sdl2.SDL_GetRenderer
_sdl2_getrenderer.argtypes = [SDL_Window_p]
_sdl2_getrenderer.restype = SDL_Renderer_p
def sdl_getrenderer(window) -> SDL_Renderer_p:
    return _sdl2_getrenderer(window)

def sdl_setrenderdrawblendmode(renderer, blendmode):
    _sdl2.SDL_SetRenderDrawBlendMode(renderer, blendmode)

_sdl2_getwindowfromid = _sdl2.SDL_GetWindowFromID
_sdl2_getwindowfromid.argtypes = [ctypes.c_uint32]
_sdl2_getwindowfromid.restype = SDL_Window_p
def sdl_getwindowfromid(id) -> SDL_Window_p:
    return _sdl2_getwindowfromid(ctypes.c_uint32(id))

def sdl_capturemouse(enabled):
    _sdl2.SDL_CaptureMouse(ctypes.c_bool(enabled))

def sdl_eventstate(type, state):
    return _sdl2.SDL_EventState(type, state)

_sdl2_getwindowwminfo = _sdl2.SDL_GetWindowWMInfo
_sdl2_getwindowwminfo.restype = ctypes.c_int
def sdl_getwindowwminfo(window):
    info = SDL_SysWMinfo()
    SDL_VERSION(info.version)
    if _sdl2_getwindowwminfo(window, ctypes.byref(info)):
        return info

SDL_EventFilter = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(SDL_Event))

def sdl_addeventwatch(filter: SDL_EventFilter, userdata: c_void_p):
    _sdl2.SDL_AddEventWatch(filter, userdata)

def sdl_deleventwatch(filter: SDL_EventFilter, userdata: c_void_p):
    _sdl2.SDL_DelEventWatch(filter, userdata)

os.chdir(_cwd)
