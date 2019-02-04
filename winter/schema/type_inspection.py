import collections
import datetime
import decimal
import enum
import inspect
import typing
import uuid
from collections import OrderedDict

import dataclasses
from drf_yasg import openapi
from rest_framework.settings import api_settings as rest_settings

from winter.type_utils import NoneType
from winter.type_utils import UnionType
from winter.type_utils import get_origin_type
from winter.type_utils import is_optional

TYPE_DECIMAL = openapi.TYPE_STRING if rest_settings.COERCE_DECIMAL_TO_STRING else openapi.TYPE_NUMBER
TYPE_NONE = 'none'
_resolvers_by_type: typing.Dict[typing.Type, typing.Tuple[typing.Callable, typing.Optional[typing.Callable]]] = {}


def register(*types: typing.Tuple[typing.Type], checker=None):
    def wrapper(func):
        for type_ in types:
            _resolvers_by_type[type_] = func, checker
        return func

    return wrapper


class InspectorNotFound(Exception):

    def __init__(self, hint_cls):
        self.hint_cls = hint_cls

    def __str__(self):
        return f'Unknown type: {self.hint_cls}'


@dataclasses.dataclass
class TypeInfo:
    type_: str
    format_: typing.Optional[str] = None
    child: typing.Optional['TypeInfo'] = None
    nullable: bool = False
    properties: typing.Dict[str, 'TypeInfo'] = dataclasses.field(default_factory=OrderedDict)
    enum: list = None

    def as_dict(self):
        data = {
            'type': self.type_,
        }
        if self.format_ is not None:
            data['format'] = self.format_

        if self.child is not None:
            data['items'] = self.child.as_dict()

        if self.nullable:
            data['x-nullable'] = True

        if self.enum is not None:
            data['enum'] = self.enum

        if self.properties:
            data['properties'] = {key: value.as_dict() for key, value in self.properties.items()}

        return data

    def get_openapi_schema(self):
        return openapi.Schema(**self.as_dict())


# noinspection PyUnusedLocal
@register(bool)
def inspect_bool(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_BOOLEAN)


# noinspection PyUnusedLocal
@register(NoneType)
def inspect_none(hint_class) -> TypeInfo:
    return TypeInfo(TYPE_NONE)


# noinspection PyUnusedLocal
@register(int)
def inspect_int(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_INTEGER)


# noinspection PyUnusedLocal
@register(str, bytes)
def inspect_str(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_STRING)


# noinspection PyUnusedLocal
@register(float)
def inspect_float(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_NUMBER)


# noinspection PyUnusedLocal
@register(dict)
def inspect_dict(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_OBJECT)


# noinspection PyUnusedLocal
@register(decimal.Decimal)
def inspect_decimal(hint_class) -> TypeInfo:
    return TypeInfo(TYPE_DECIMAL, openapi.FORMAT_DECIMAL)


# noinspection PyUnusedLocal
@register(uuid.UUID)
def inspect_uuid(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_UUID)


# noinspection PyUnusedLocal
@register(datetime.datetime)
def inspect_datetime(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_DATETIME)


# noinspection PyUnusedLocal
@register(datetime.date)
def inspect_date(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_DATE)


# noinspection PyUnusedLocal
@register(list, tuple, collections.Iterable)
def inspect_iterable(hint_class) -> TypeInfo:
    args = getattr(hint_class, '__args__', None)
    child_class = args[0] if args else str
    child_type_info = inspect_type(child_class)
    return TypeInfo(openapi.TYPE_ARRAY, child=child_type_info)


@register(enum.IntEnum, enum.Enum)
def inspect_enum(enum_class: typing.Type[enum.Enum]) -> TypeInfo:
    enum_values = [entry.value for entry in enum_class]
    # Try to infer type based on enum values
    enum_value_types = {type(v) for v in enum_values}

    if len(enum_value_types) == 1:
        type_info = inspect_type(enum_value_types.pop())
    else:
        type_info = TypeInfo(openapi.TYPE_STRING)
    type_info.enum = enum_values
    return type_info


@register(UnionType, checker=is_optional)
def inspect_optional(hint_class) -> TypeInfo:
    child_type = hint_class.__args__[0]
    type_info = inspect_type(child_type)
    type_info.nullable = True
    return type_info


@register(object, checker=dataclasses.is_dataclass)
def inspect_dataclass(hint_class) -> TypeInfo:
    fields = dataclasses.fields(hint_class)

    properties = {
        field.name: inspect_type(field.type)
        for field in fields
    }
    return TypeInfo(type_=openapi.TYPE_OBJECT, properties=properties)


def inspect_type(hint_class) -> TypeInfo:
    origin_type = get_origin_type(hint_class)

    if inspect.isclass(origin_type):
        types = origin_type.mro()
    else:
        types = type(origin_type).mro()

    for type_ in types:
        data = _resolvers_by_type.get(type_)
        if data is None:
            continue
        resolver, checker = data

        if checker is None or checker(hint_class):
            return resolver(hint_class)

    raise InspectorNotFound(hint_class)
