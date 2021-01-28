
from copy import copy
from ._mouse import *
from .pygame import runner

def pressed():
    return copy(runner.mouses)
