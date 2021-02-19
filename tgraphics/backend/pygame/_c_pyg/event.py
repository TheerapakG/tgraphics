import copy
import ctypes
import os
from pathlib import Path
import pygame
import sys

from .._c_sdl.sdl2 import *

PYGAMEAPI_EVENT_NUMSLOTS = 6 # pygame/src_c/_pygame.h

IMPPREFIX = "pygame."
PYGAMEAPI_LOCAL_ENTRY = "_PYGAME_C_API"

def PG_CAPSULE_NAME(m):
    return ''.join([IMPPREFIX, m, ".", PYGAMEAPI_LOCAL_ENTRY])

ctypes.pythonapi.PyCapsule_GetPointer.argtypes = [ctypes.py_object, ctypes.c_char_p]
ctypes.pythonapi.PyCapsule_GetPointer.restype = ctypes.c_void_p

_pyg_event_capsule = getattr(pygame.event, PYGAMEAPI_LOCAL_ENTRY)
_pyg_event_capi = ctypes.cast(
    ctypes.pythonapi.PyCapsule_GetPointer(_pyg_event_capsule, PG_CAPSULE_NAME("event").encode('utf-8')),
    ctypes.POINTER(ctypes.c_void_p)
)

_pyg_event_new_proto = ctypes.PYFUNCTYPE(ctypes.py_object, ctypes.POINTER(SDL_Event))
_pyg_event_new = _pyg_event_new_proto(_pyg_event_capi[1])
def pgevent_new(event):
    return _pyg_event_new(event)
