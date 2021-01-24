from importlib import import_module
import sys
from types import ModuleType
from typing import Union

_BackendModule = None

class UninitializedBackendError(Exception):
    pass

def init_with_backend(backend: Union[str, ModuleType]) -> None:
    global _BackendModule
    if _BackendModule:
        uninit()

    if isinstance(backend, str):
        # explore in ext for the specified backend
        backend = import_module(f'..media_backend.{backend}', __name__)

    _BackendModule = backend

def uninit() -> None:
    global _BackendModule
    if _BackendModule:
        _BackendModule = None
    else:
        raise UninitializedBackendError()

def _current_backend():
    if _BackendModule:
        return _BackendModule
    raise UninitializedBackendError()

# PEP562
def __getattr__(name: str):
    if name in globals():
        return globals()[name]
    # not implemented/cannot be abstracted in core
    return getattr(_current_backend(), name) # pylint: disable=undefined-variable

def __dir__():
    _dir = ['init_with_backend', 'uninit']
    if _current_backend():
        _dir.extend(n for n in dir(_current_backend()) if not n.startswith('_'))
