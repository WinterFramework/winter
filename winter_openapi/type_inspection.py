import dataclasses
import datetime
import decimal
import enum
import inspect
import types
import uuid
from collections import OrderedDict
from collections.abc import Iterable
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from drf_yasg import openapi

from winter.core.utils import has_nested_type
from winter.core.utils.typing import get_origin_type
from winter.core.utils.typing import is_any
from winter.core.utils.typing import is_optional
from winter.core.utils.typing import is_type_var

_inspectors_by_type: Dict[
    Type,
    List[Tuple[Callable, Optional[Callable]]],
] = {}


TYPE_ANY_VALUE = 'AnyValue'


def register_type_inspector(*types_: Type, checker: Callable = None, func: Callable = None):
    if func is None:
        return lambda func: register_type_inspector(*types_, checker=checker, func=func)

    for type_ in types_:
        callables = _inspectors_by_type.setdefault(type_, [])
        callables.append((func, checker))
    return func


class InspectorNotFound(Exception):

    def __init__(self, hint_cls):
        self.hint_cls = hint_cls

    def __str__(self):
        return f'Unknown type: {self.hint_cls}'


@dataclasses.dataclass
class TypeInfo:
    type_: str
    format_: Optional[str] = None
    child: Optional['TypeInfo'] = None
    nullable: bool = False
    properties: Dict[str, 'TypeInfo'] = dataclasses.field(default_factory=OrderedDict)
    enum: Optional[list] = None

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.as_dict() == other.as_dict()

    def as_dict(self):
        data = {
            # AnyValue map to Object in OpenApi 2.0
            'type': openapi.TYPE_OBJECT if self.type_ == TYPE_ANY_VALUE else self.type_,
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
@register_type_inspector(bool)
def inspect_bool(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_BOOLEAN)


# noinspection PyUnusedLocal
@register_type_inspector(int)
def inspect_int(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_INTEGER)


# noinspection PyUnusedLocal
@register_type_inspector(bytes)
def inspect_bytes(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_BINARY)


# noinspection PyUnusedLocal
@register_type_inspector(str)
def inspect_str(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_STRING)


# noinspection PyUnusedLocal
@register_type_inspector(float)
def inspect_float(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_NUMBER)


# noinspection PyUnusedLocal
@register_type_inspector(dict)
def inspect_dict(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_OBJECT)


# noinspection PyUnusedLocal
@register_type_inspector(object, checker=is_any)
def inspect_any(hint_class) -> TypeInfo:
    return TypeInfo(TYPE_ANY_VALUE)


# noinspection PyUnusedLocal
@register_type_inspector(object, checker=is_type_var)
def inspect_type_var(hint_class) -> TypeInfo:
    return TypeInfo(TYPE_ANY_VALUE)


# noinspection PyUnusedLocal
@register_type_inspector(decimal.Decimal)
def inspect_decimal(hint_class) -> TypeInfo:
    from rest_framework.settings import api_settings
    TYPE_DECIMAL = openapi.TYPE_STRING if api_settings.COERCE_DECIMAL_TO_STRING else openapi.TYPE_NUMBER
    return TypeInfo(TYPE_DECIMAL, openapi.FORMAT_DECIMAL)


# noinspection PyUnusedLocal
@register_type_inspector(uuid.UUID)
def inspect_uuid(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_UUID)


# noinspection PyUnusedLocal
@register_type_inspector(datetime.datetime)
def inspect_datetime(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_DATETIME)


# noinspection PyUnusedLocal
@register_type_inspector(datetime.date)
def inspect_date(hint_class) -> TypeInfo:
    return TypeInfo(openapi.TYPE_STRING, openapi.FORMAT_DATE)


# noinspection PyUnusedLocal
@register_type_inspector(list, tuple, set, Iterable)
def inspect_iterable(hint_class) -> TypeInfo:
    args = getattr(hint_class, '__args__', None)
    if args is None:
        return TypeInfo(openapi.TYPE_ARRAY, child=TypeInfo(TYPE_ANY_VALUE))
    child_class = args[0]
    child_type_info = inspect_type(child_class)
    return TypeInfo(openapi.TYPE_ARRAY, child=child_type_info)


@register_type_inspector(enum.IntEnum, enum.Enum)
def inspect_enum(enum_class: Type[enum.Enum]) -> TypeInfo:
    enum_values = [entry.value for entry in enum_class]
    # Try to infer type based on enum values
    enum_value_types = {type(v) for v in enum_values}

    if len(enum_value_types) == 1:
        type_info = inspect_type(enum_value_types.pop())
    else:
        type_info = TypeInfo(openapi.TYPE_STRING)
    type_info.enum = enum_values
    return type_info


@register_type_inspector(object, checker=is_optional)
def inspect_optional(hint_class) -> TypeInfo:
    child_type = hint_class.__args__[0]
    type_info = inspect_type(child_type)
    type_info.nullable = True
    return type_info


@register_type_inspector(object, checker=dataclasses.is_dataclass)
def inspect_dataclass(hint_class) -> TypeInfo:
    fields = dataclasses.fields(hint_class)

    properties = {
        field.name: inspect_type(field.type)
        for field in fields
    }
    return TypeInfo(type_=openapi.TYPE_OBJECT, properties=properties)


@register_type_inspector(object, checker=has_nested_type)
def inspect_type_wrapper(hint_class) -> TypeInfo:
    nested_type = hint_class._nested_type
    type_info = inspect_type(nested_type)
    return type_info


@register_type_inspector(
    types.FunctionType,
    checker=lambda instance: getattr(instance, '__supertype__', None) is not None,
)
def inspect_new_type(hint_class) -> TypeInfo:
    return inspect_type(hint_class.__supertype__)


def inspect_type(hint_class) -> TypeInfo:
    origin_type = get_origin_type(hint_class)

    types_ = origin_type.mro() if inspect.isclass(origin_type) else type(origin_type).mro()

    for type_ in types_:
        inspectors = _inspectors_by_type.get(type_, [])
        type_info = _inspect_type(hint_class, inspectors)

        if type_info is not None:
            return type_info

    raise InspectorNotFound(hint_class)


def _inspect_type(
    hint_class,
    inspectors: List[Tuple[Callable, Optional[Callable]]],
) -> Optional[TypeInfo]:
    for inspector, checker in inspectors:
        if checker is None or checker(hint_class):
            return inspector(hint_class)
