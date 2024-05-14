import warnings
import functools
from typing import Callable


def deprecated(func: Callable, msg: str):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(f'{func.__name__} is deprecated. {msg}',
                      category=DeprecationWarning,
                      stacklevel=2)
        return func(*args, **kwargs)
    return wrapper