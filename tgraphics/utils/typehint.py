import sys
assert sys.version_info[0] == 3

from typing import Type, TYPE_CHECKING, TypeVar

T = TypeVar('T')

if sys.version_info[1] < 9:
    from typing import Callable, Iterator, List, Tuple
else:
    from collections.abc import Callable, Iterator
    List = list
    Tuple = tuple

def mixin_with_typehint(base: Type[T]) -> Type[T]:
    """
    make mixin have type hinting
    """
    if TYPE_CHECKING:
        return base
    return object

