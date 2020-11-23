import os
import importlib

__all__ = []

for module in os.scandir(os.path.dirname(__file__)):
    if module.name.startswith('_'):
        continue
    if module.is_dir():
        __all__.append(module.name)
        importlib.import_module(f'.{module.name}', __name__)
        continue
    if module.is_file():
        name = os.path.splitext(module.name)[0]
        __all__.append(name)
        importlib.import_module(f'.{name}', __name__)
        
del name
del module
del os
del importlib
