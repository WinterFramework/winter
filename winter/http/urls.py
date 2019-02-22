import enum
import inspect
import types
import typing
import uuid

import uritemplate

from ..controller import ControllerMethod
from ..type_utils import get_origin_type

_regex = {}


def register_url_regex(func: types.FunctionType):
    annotations = func.__annotations__.copy()
    annotations.pop('return', None)
    assert len(annotations) == 1
    _item, type_ = annotations.popitem()
    _regex[type_] = func
    return func


def rewrite_uritemplate_with_regexps(url_path: str, methods: typing.List[ControllerMethod]) -> str:
    for variable_name in uritemplate.variables(url_path):
        arguments = (method.get_argument(variable_name) for method in methods)

        argument_types = {argument.type_ for argument in arguments if argument is not None}

        if len(argument_types) > 1:
            raise Exception(
                f'Different methods are bound to the same path variable, '
                f'but have different types annotated: {argument_types}'
            )
        regexp = get_regexp(*argument_types)
        url_path = url_path.replace(f'{{{variable_name}}}', f'(?P<{variable_name}>{regexp})')
    return url_path


def get_regexp(type_=None) -> str:
    origin_type = get_origin_type(type_)

    if not inspect.isclass(origin_type):
        origin_type = type(origin_type)

    for cls in origin_type.mro():
        func = _regex.get(cls)

        if func is not None:
            return func(type_)
    return r'[^/]+'


# noinspection PyUnusedLocal
@register_url_regex
def int_regex(cls: int):
    return r'\d+'


# noinspection PyUnusedLocal
@register_url_regex
def uuid_regex(cls: uuid.UUID):
    return r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'


@register_url_regex
def enum_regex(cls: enum.Enum):
    values = (f'({e.value})' for e in cls)
    return '(' + '|'.join(values) + ')'
