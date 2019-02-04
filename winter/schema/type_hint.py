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


@dataclasses.dataclass
class YASGTypeInfo:
    type_: str
    format_: typing.Optional[str] = None
    child: typing.Optional['YASGTypeInfo'] = None
    nullable: bool = False
    properties: typing.Dict[str, 'YASGTypeInfo'] = dataclasses.field(default_factory=OrderedDict)
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


# noinspection PyUnusedLocal
@register(bool)
def bool_resolver(hint_class) -> YASGTypeInfo:
    return YASGTypeInfo(openapi.TYPE_BOOLEAN)


# noinspection PyUnusedLocal
@register(NoneType)
def none_resolver(hint_class) -> YASGTypeInfo:
    return YASGTypeInfo(TYPE_NONE)


# noinspection PyUnusedLocal
@register(int)
def int_resolver(hint_class) -> YASGTypeInfo:
    return YASGTypeInfo(openapi.TYPE_INTEGER)


# noinspection PyUnusedLocal
@register(str)
def str_resolver(hint_class) -> YASGTypeInfo:
    return YASGTypeInfo(openapi.TYPE_STRING)


# noinspection PyUnusedLocal
@register(float)
def float_resolver(hint_class) -> YASGTypeInfo:
    return YASGTypeInfo(openapi.TYPE_NUMBER)


# noinspection PyUnusedLocal
@register(dict)
def dict_resolver(hint_class) -> YASGTypeInfo:
    return YASGTypeInfo(openapi.TYPE_OBJECT)


# noinspection PyUnusedLocal
@register(decimal.Decimal)
def decimal_resolver(hint_class) -> YASGTypeInfo:
    return YASGTypeInfo(TYPE_DECIMAL, openapi.FORMAT_DECIMAL)


# noinspection PyUnusedLocal
@register(uuid.UUID)
def uuid_resolver(hint_class) -> YASGTypeInfo:
    return YASGTypeInfo(openapi.TYPE_STRING, openapi.FORMAT_UUID)


# noinspection PyUnusedLocal
@register(datetime.datetime)
def datetime_resolver(hint_class) -> YASGTypeInfo:
    return YASGTypeInfo(openapi.TYPE_STRING, openapi.FORMAT_DATETIME)


# noinspection PyUnusedLocal
@register(datetime.date)
def date_resolver(hint_class) -> YASGTypeInfo:
    return YASGTypeInfo(openapi.TYPE_STRING, openapi.FORMAT_DATE)


# noinspection PyUnusedLocal
@register(list, tuple, collections.Iterable, collections.Sequence, collections.Set)
def iterable_resolver(hint_class) -> YASGTypeInfo:
    args = getattr(hint_class, '__args__', None)
    child_class = args[0] if args else str
    child_type_info = get_basic_type_info_from_hint(child_class)
    return YASGTypeInfo(openapi.TYPE_ARRAY, child=child_type_info)


@register(enum.IntEnum)
def intenum_resolver(enum_class: typing.Type[enum.IntEnum]) -> YASGTypeInfo:
    return enum_resolver(enum_class)


@register(enum.Enum)
def enum_resolver(enum_class: typing.Type[enum.Enum]) -> YASGTypeInfo:
    enum_values = [entry.value for entry in enum_class]
    # Try to infer type based on enum values
    enum_value_types = {type(v) for v in enum_values}

    if len(enum_value_types) == 1:
        type_info = get_basic_type_info_from_hint(enum_value_types.pop())
    else:
        type_info = YASGTypeInfo(openapi.TYPE_STRING)
    type_info.enum = enum_values
    return type_info


@register(UnionType, checker=is_optional)
def union_resolver(hint_class) -> YASGTypeInfo:
    child_type = hint_class.__args__[0]
    type_info = get_basic_type_info_from_hint(child_type)
    type_info.nullable = True
    return type_info


@register(object, checker=dataclasses.is_dataclass)
def dataclass_resolver(hint_class) -> YASGTypeInfo:
    fields = dataclasses.fields(hint_class)

    properties = {
        field.name: get_basic_type_info_from_hint(field.type)
        for field in fields
    }
    return YASGTypeInfo(type_=openapi.TYPE_OBJECT, properties=properties)


def get_basic_type_info_from_hint(hint_class) -> typing.Optional[YASGTypeInfo]:
    """Given a class (eg from a SerializerMethodField's return type hint,
    return its basic type information - ``type``, ``format``, ``pattern``,
    and any applicable min/max limit values.

    :param hint_class: the class
    :return: the extracted attributes as a dictionary, or ``None`` if the field type is not known
    :rtype: OrderedDict
    """
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

    raise ValueError(f'Unknown type: {hint_class}')
