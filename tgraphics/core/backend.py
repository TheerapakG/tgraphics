from .core import _current_backend

# PEP562
def __getattr__(name: str):
    # not implemented/cannot be abstracted in core
    return getattr(_current_backend(), name) # pylint: disable=undefined-variable
    