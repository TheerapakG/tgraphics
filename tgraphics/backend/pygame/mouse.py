
from copy import copy
from ._mouse import *
from .pygame import _mouses

def pressed():
    return copy(_mouses)
