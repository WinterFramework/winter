import dataclasses
import datetime
import decimal
import enum
import inspect
import types
import typing
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
from strenum import StrEnum

from winter.core.docstring import Docstring
from winter.core.utils import has_nested_type
from winter.core.utils.typing import get_origin_type, get_generic_args
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
    properties_defaults: Dict[str, object] = dataclasses.field(default_factory=dict)
    enum: Optional[list] = None
    title: str = ''
    description: str = ''

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.as_dict() == other.as_dict()

    def as_dict(self, output: bool = True):
        data = {
            # AnyValue map to Object in OpenApi 2.0
            'type': openapi.TYPE_OBJECT if self.type_ == TYPE_ANY_VALUE else self.type_,
        }

        if self.title:
            if output:
                data['title'] = self.title
            else:
                data['title'] = f'{self.title}Input'

        if self.description:
            data['description'] = self.description

        if self.format_ is not None:
            data['format'] = self.format_

        if self.child is not None:
            data['items'] = self.child.as_dict(output)

        if self.nullable:
            data['x-nullable'] = True

        if self.enum is not None:
            data['enum'] = self.enum

        if self.properties:
            data['properties'] = {key: value.as_dict(output) for key, value in self.properties.items()}

        if output:
            required_properties = list(self.properties)
        else:
            required_properties = [
                property_name
                for property_name in self.properties
                if property_name not in self.properties_defaults
            ]

        if required_properties:
            data['required'] = required_properties

        return data

    def get_openapi_schema(self, output: bool) -> openapi.Schema:
        return openapi.Schema(**self.as_dict(output))


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
def inspect_type_var(hint_class) -> TypeInfo:  # pragma: no cover
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
    args = get_generic_args(hint_class)
    if not args:
        return TypeInfo(openapi.TYPE_ARRAY, child=TypeInfo(TYPE_ANY_VALUE))
    child_class = args[0]
    child_type_info = inspect_type(child_class)
    return TypeInfo(openapi.TYPE_ARRAY, child=child_type_info)


@register_type_inspector(enum.IntEnum, StrEnum, enum.Enum)
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
    cls = hint_class if isinstance(hint_class, type) else type(hint_class)
    title = cls.__name__
    docstring = Docstring(cls.__doc__)
    description = docstring.get_description()

    fields = dataclasses.fields(hint_class)

    properties = {
        field.name: inspect_type(field.type)
        for field in fields
    }
    for field_name, type_info in properties.items():
        field_description = docstring.get_argument_description(field_name)
        if field_description:
            type_info.description = field_description

    defaults = {
        field.name: field.default
        for field in fields
        if field.default != dataclasses.MISSING
    }

    return TypeInfo(
        type_=openapi.TYPE_OBJECT,
        properties=properties,
        properties_defaults=defaults,
        title=title,
        description=description,
    )


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


@register_type_inspector(
    typing.NewType,
    checker=lambda instance: getattr(instance, '__supertype__', None) is not None,
)
def inspect_new_type_class(hint_class) -> TypeInfo:
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
