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
        module = importlib.import_module(f'.{name}', __name__)
        exports = [s for s in dir(module) if not s.startswith('_')]
        globals().update({s:getattr(module, s) for s in exports})
        __all__.extend(exports)
        del exports
        del name
        
del module
del os
del importlib
