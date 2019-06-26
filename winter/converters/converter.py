import datetime
import enum
import inspect
import typing

import dataclasses
from dateutil import parser

from ..type_utils import get_origin_type
from ..type_utils import is_optional

_converters = {}


class ConvertError(Exception):

    def __init__(self, errors):
        self.errors = errors


def converter(type_: typing.Type, validator: typing.Callable = None):
    def wrapper(func):
        converters = _converters.setdefault(type_, [])
        converters.append((func, validator))
        return func

    return wrapper


def convert(data, hint_class):
    origin_type = get_origin_type(hint_class)

    types_ = origin_type.mro() if inspect.isclass(origin_type) else type(origin_type).mro()

    for type_ in types_:
        converters = _converters.get(type_, [])

        for converter_, checker in converters:
            if checker is None or checker(hint_class):
                return converter_(data, hint_class)

    raise ConvertError(f'Cannot convert "{data}"')


@converter(object, validator=is_optional)
def optional_converter(data, type_):
    if data is None:
        return None
    type_ = type_.__args__[0]
    return convert(data, type_)


@converter(object, validator=dataclasses.is_dataclass)
def dataclass_converter(data: typing.Dict[str, typing.Any], type_):
    if not isinstance(data, dict):
        raise ConvertError(f'Cannot convert "{data}"')

    errors = {}
    converted_data = {}
    missing_fields = []

    for field in dataclasses.fields(type_):
        field_data = data.get(field.name, dataclasses.MISSING)

        if field_data is dataclasses.MISSING:
            if is_optional(field.type):
                field_data = None
            else:
                missing_fields.append(field.name)
                continue
        try:
            field_data = convert(field_data, field.type)
        except ConvertError as e:
            errors[field.name] = e.errors
        else:
            converted_data[field.name] = field_data
    if missing_fields:
        missing_fields = '", "'.join(missing_fields)
        errors['non_field_error'] = f'Missing fields: "{missing_fields}"'

    if errors:
        raise ConvertError(errors)
    return type_(**converted_data)


@converter(int)
def int_converter(value, type_) -> int:
    try:
        return type_(value)
    except (TypeError, ValueError):
        raise ConvertError(f'Cannot convert "{value}" to integer')


@converter(str)
def convert_srt(value, type_) -> str:
    return type_(value)


@converter(enum.Enum)
def convert_enum(value, type_):
    try:
        return type_(value)
    except ValueError:
        allowed_values = '", "'.join(map(str, (item.value for item in type_)))
        raise ConvertError(f'Value not in allowed values("{allowed_values}"): "{value}"')


# noinspection PyUnusedLocal
@converter(datetime.date)
def convert_date(value, type_):
    try:
        return parser.parse(value).date()
    except (ValueError, TypeError):
        raise ConvertError(f'Cannot convert "{value}" to date')


# noinspection PyUnusedLocal
@converter(datetime.datetime)
def convert_datetime(value, type_):
    try:
        return parser.parse(value)
    except (ValueError, TypeError):
        raise ConvertError(f'Cannot convert "{value}" to datetime')


@converter(list)
def convert_list(value, type_):
    child_types = getattr(type_, '__args__', [])
    child_type = child_types[0] if child_types else str

    if not isinstance(value, typing.Iterable):
        raise ConvertError(f'Cannot convert "{value}" to list')

    updated_value = [
        convert(item, child_type)
        for item in value
    ]
    return updated_value


@converter(set)
def convert_set(value, type_):
    child_types = getattr(type_, '__args__', [])
    child_type = child_types[0] if child_types else str

    if not isinstance(value, typing.Iterable):
        raise ConvertError(f'Cannot convert "{value}" to set')

    updated_value = {
        convert(item, child_type)
        for item in value
    }
    return updated_value
