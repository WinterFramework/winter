import inspect
import sys
from typing import Iterable
from typing import Union

NoneType = type(None)
UnionType = type(Union)


def is_optional(typing: object) -> bool:
    return is_union(typing) and NoneType in (getattr(typing, '__args__', []) or [])


def is_iterable_type(typing: object) -> bool:
    """Note that str is not iterable here"""
    if is_union(typing):
        return all(is_iterable_type(arg) for arg in typing.__args__ if arg is not NoneType)

    return is_origin_type_subclasses(typing, Iterable) and not is_origin_type_subclasses(typing, str)


def is_union(typing: object) -> bool:
    return get_origin_type(typing) == Union


def get_origin_type(hint_class):
    return getattr(hint_class, '__origin__', None) or hint_class


def is_origin_type_subclasses(hint_class, check_class):
    origin_type = get_origin_type(hint_class)
    return inspect.isclass(origin_type) and issubclass(origin_type, check_class)


def get_type_name(type_):
    if inspect.isclass(type_):
        return type_.__name__

    if is_optional(type_):
        base_type = type_.__args__[0]
        base_type_name = get_type_name(base_type)
        return f'Optional[{base_type_name}]'

    type_name = repr(type_)
    if type_name.startswith('typing.'):
        type_name = type_name[7:]
        return type_name

    return type(type_).__name__


def get_generic_args(type_):
    if sys.version_info >= (3, 8):
        from typing import get_args
        return get_args(type_)
    if sys.version_info >= (3, 7):
        return type_.__args__
    return type_.__args__
