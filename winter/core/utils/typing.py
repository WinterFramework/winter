import inspect
import types
from typing import Iterable
from typing import TypeVar
from typing import Union
from typing import get_origin

NoneType = type(None)


def is_optional(type_: object) -> bool:
    return is_union(type_) and NoneType in get_union_args(type_)


def is_any(type_: object) -> bool:
    return str(type_) == 'typing.Any'


def is_type_var(type_: object) -> bool:
    return type(type_) == TypeVar


def is_iterable_type(type_: object) -> bool:
    """Note that str is not iterable here"""
    if is_union(type_):
        return all(is_iterable_type(arg) for arg in type_.__args__ if arg is not NoneType)

    return is_origin_type_subclasses(type_, Iterable) and not is_origin_type_subclasses(type_, str)


def is_union(type_: object) -> bool:
    return get_origin_type(type_) in (Union, types.UnionType)


def get_union_args(type_: object) -> list:
    return getattr(type_, '__args__', []) or []


def get_origin_type(hint_class):
    return get_origin(hint_class) or hint_class


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

    if type(type_) in (types.GenericAlias, types.UnionType):
        return type_name

    return type(type_).__name__
