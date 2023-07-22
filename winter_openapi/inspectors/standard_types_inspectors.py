import dataclasses
import datetime
import decimal
import enum
import types
import typing
import uuid
from collections.abc import Iterable
from typing import Type

from strenum import StrEnum

from winter.core.docstring import Docstring
from winter.core.json import Undefined
from winter.core.utils import has_nested_type
from winter.core.utils.typing import get_generic_args
from winter.core.utils.typing import get_union_args
from winter.core.utils.typing import is_any
from winter.core.utils.typing import is_optional
from winter.core.utils.typing import is_type_var
from winter.core.utils.typing import is_union
from winter_openapi.inspection.data_formats import DataFormat
from winter_openapi.inspection.data_types import DataTypes
from winter_openapi.inspection.inspection import inspect_type
from winter_openapi.inspection.inspection import register_type_inspector
from winter_openapi.inspection.type_info import TypeInfo


# noinspection PyUnusedLocal
@register_type_inspector(bool)
def inspect_bool(hint_class) -> TypeInfo:
    return TypeInfo(type_=DataTypes.BOOLEAN)


# noinspection PyUnusedLocal
@register_type_inspector(int)
def inspect_int(hint_class) -> TypeInfo:
    return TypeInfo(type_=DataTypes.INTEGER, format_=DataFormat.INT32)


# noinspection PyUnusedLocal
@register_type_inspector(bytes)
def inspect_bytes(hint_class) -> TypeInfo:
    return TypeInfo(type_=DataTypes.STRING, format_=DataFormat.BASE64)


# noinspection PyUnusedLocal
@register_type_inspector(str)
def inspect_str(hint_class) -> TypeInfo:
    return TypeInfo(type_=DataTypes.STRING)


# noinspection PyUnusedLocal
@register_type_inspector(float)
def inspect_float(hint_class) -> TypeInfo:
    return TypeInfo(type_=DataTypes.NUMBER, format_=DataFormat.FLOAT)


# noinspection PyUnusedLocal
@register_type_inspector(dict)
def inspect_dict(hint_class) -> TypeInfo:
    return TypeInfo(type_=DataTypes.OBJECT)


# noinspection PyUnusedLocal
@register_type_inspector(object, checker=is_any)
def inspect_any(hint_class) -> TypeInfo:
    return TypeInfo(type_=DataTypes.ANY)


# noinspection PyUnusedLocal
@register_type_inspector(object, checker=is_type_var)
def inspect_type_var(hint_class) -> TypeInfo:
    return TypeInfo(type_=DataTypes.ANY)


# noinspection PyUnusedLocal
@register_type_inspector(decimal.Decimal)
def inspect_decimal(hint_class) -> TypeInfo:
    return TypeInfo(type_=DataTypes.STRING, format_=DataFormat.DECIMAL)


# noinspection PyUnusedLocal
@register_type_inspector(uuid.UUID)
def inspect_uuid(hint_class) -> TypeInfo:
    return TypeInfo(type_=DataTypes.STRING, format_=DataFormat.UUID)


# noinspection PyUnusedLocal
@register_type_inspector(datetime.datetime)
def inspect_datetime(hint_class) -> TypeInfo:
    return TypeInfo(type_=DataTypes.STRING, format_=DataFormat.DATETIME)


# noinspection PyUnusedLocal
@register_type_inspector(datetime.date)
def inspect_date(hint_class) -> TypeInfo:
    return TypeInfo(type_=DataTypes.STRING, format_=DataFormat.DATE)


# noinspection PyUnusedLocal
@register_type_inspector(list, tuple, set, Iterable)
def inspect_iterable(hint_class) -> TypeInfo:
    args = get_generic_args(hint_class)
    if not args:
        return TypeInfo(type_=DataTypes.ARRAY, child=TypeInfo(type_=DataTypes.ANY))
    child_class = args[0]
    child_schema = inspect_type(child_class)
    return TypeInfo(type_=DataTypes.ARRAY, child=child_schema)


@register_type_inspector(enum.IntEnum, StrEnum, enum.Enum)
def inspect_enum(enum_class: Type[enum.Enum]) -> TypeInfo:
    enum_values = [entry.value for entry in enum_class]
    # Try to infer type_ based on enum values
    enum_value_types = {type(v) for v in enum_values}

    if len(enum_value_types) == 1:
        schema = inspect_type(enum_value_types.pop())
    else:
        schema = TypeInfo(type_=DataTypes.STRING)
    schema.enum = enum_values
    return schema


@register_type_inspector(object, checker=is_optional)
def inspect_optional(hint_class) -> TypeInfo:
    child_type = hint_class.__args__[0]
    schema = inspect_type(child_type)
    schema.nullable = True
    return schema


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
        type_=DataTypes.OBJECT,
        properties=properties,
        properties_defaults=defaults,
        title=title,
        description=description,
    )


@register_type_inspector(object, checker=has_nested_type)
def inspect_type_wrapper(hint_class) -> TypeInfo:
    nested_type = hint_class._nested_type
    schema = inspect_type(nested_type)
    return schema


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


def can_be_undefined(type_):
    return is_union(type_) and Undefined in get_union_args(type_)


@register_type_inspector(object, checker=can_be_undefined)
def inspect_can_be_undefined(hint_class) -> TypeInfo:
    union_args = get_union_args(hint_class)
    assert len(union_args) == 2, 'Union with Undefined must have 2 args'
    value_type = union_args[0] if union_args[0] is not Undefined else union_args[1]
    type_info = inspect_type(value_type)
    type_info.can_be_undefined = True
    return type_info
