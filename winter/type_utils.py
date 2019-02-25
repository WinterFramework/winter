import inspect
from typing import Iterable
from typing import Union

NoneType = type(None)
UnionType = type(Union)


def is_optional(typing: object) -> bool:
    return is_union(typing) and NoneType in typing.__args__


def is_iterable(typing: object) -> bool:
    """Note that str is not iterable here"""
    if is_union(typing):
        return all(is_iterable(arg) for arg in typing.__args__ if arg is not NoneType)

    return is_origin_type_subclasses(typing, Iterable) and not is_origin_type_subclasses(typing, str)


def is_union(typing: object) -> bool:
    return get_origin_type(typing) == Union


def get_origin_type(hint_class):
    return getattr(hint_class, '__origin__', None) or hint_class


def is_origin_type_subclasses(hint_class, check_class):
    origin_type = get_origin_type(hint_class)
    return inspect.isclass(origin_type) and issubclass(origin_type, check_class)
