from . import common

import sys

_first_level_obj = [getattr(common, s) for s in dir(common) if not s.startswith('_')]

for s in _first_level_obj:
    for t in dir(s):
        if not t.startswith('_') and hasattr(getattr(s, t), '__module__') and sys.modules[getattr(s, t).__module__] is s:
            globals()[t] = getattr(s, t)

del t
del s
del sys

from . import shapes
from . import text

__all__ = [s for s in dir() if not s.startswith('_')]
