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
        backend = import_module(f'...backend.{backend}', __name__)

    backend.init()
    _BackendModule = backend

def uninit() -> None:
    global _BackendModule
    if _BackendModule:
        _BackendModule.uninit()
        _BackendModule = None
    else:
        raise UninitializedBackendError()

def _current_backend():
    if _BackendModule:
        return _BackendModule
    raise UninitializedBackendError()
