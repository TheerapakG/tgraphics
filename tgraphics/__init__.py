from .core import *
from .elements import *

TGRAPHICS_VERSION = '0.0.1.dev1'
print(f'Tgraphics {TGRAPHICS_VERSION} by TheerapakG')

__all__ = [s for s in dir() if not s.startswith('_')]
