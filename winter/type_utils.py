import inspect
from typing import Iterable
from typing import Type
from typing import Union


def is_optional(type_: Type) -> bool:
    return is_union(type_) and type(None) in type_.__args__


def is_iterable(type_: Type) -> bool:
    """Note that str is not iterable here"""
    if is_union(type_):
        none_type = type(None)
        return all(is_iterable(arg) for arg in type_.__args__ if arg != none_type)

    return is_origin_type_subclasses(type_, Iterable) and not is_origin_type_subclasses(type_, str)


def is_union(type_: Type) -> bool:
    return get_origin_type(type_) == Union


def get_origin_type(hint_class):
    return getattr(hint_class, '__origin__', None) or hint_class


def is_origin_type_subclasses(hint_class, check_class):
    origin_type = get_origin_type(hint_class)
    if not inspect.isclass(origin_type):
        return False
    return issubclass(origin_type, check_class)
