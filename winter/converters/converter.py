import datetime
import decimal
import enum
import inspect
import re
import typing
import uuid

import dataclasses
from dateutil import parser
from .convert_exception import ConvertException
from ..type_utils import get_origin_type
from ..type_utils import is_optional

_converters = {}

Item = typing.TypeVar('Item')
uuid_regexp = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


class MissingException(Exception):
    pass


def converter(type_: typing.Type, validator: typing.Callable = None):
    def wrapper(func):
        converters = _converters.setdefault(type_, [])
        converters.append((func, validator))
        return func

    return wrapper


def convert(value, hint_class: typing.Type[Item]) -> Item:
    origin_type = get_origin_type(hint_class)

    types_ = origin_type.mro() if inspect.isclass(origin_type) else type(origin_type).mro()

    for type_ in types_:
        result = _convert(value, hint_class, type_)
        if result is not dataclasses.MISSING:
            return result
    raise ConvertException.invalid_type(value)


def _convert(value, hint_class: typing.Type[Item], type_: typing.Type) -> typing.Optional[Item]:
    converters = _converters.get(type_, [])

    for converter_, checker in converters:
        if checker is None or checker(hint_class):
            return converter_(value, hint_class)
    return dataclasses.MISSING


@converter(object, validator=is_optional)
def convert_optional(value, type_: typing.Type[Item]) -> Item:
    if value is None:
        return None
    type_ = type_.__args__[0]
    return convert(value, type_)


@converter(object, validator=dataclasses.is_dataclass)
def convert_dataclass(value: typing.Dict[str, typing.Any], type_: typing.Type[Item]) -> Item:
    if not isinstance(value, typing.Mapping):
        raise ConvertException.invalid_type(value, 'object')

    errors = {}
    converted_data = {}
    missing_fields = []

    for field in dataclasses.fields(type_):
        field_data = value.get(field.name, dataclasses.MISSING)
        field_data = convert_dataclass_field(field_data, field, missing_fields, errors)
        if field_data is not dataclasses.MISSING:
            converted_data[field.name] = field_data

    if missing_fields:
        missing_fields = '", "'.join(missing_fields)
        errors[ConvertException.NON_FIELD_ERROR] = ConvertException.MISSING_FIELDS_PATTERN.format(
            missing_fields=missing_fields,
        )
    raise_if_errors(errors)
    return type_(**converted_data)


def raise_if_errors(errors: typing.Dict[str, str]):
    if errors:
        raise ConvertException(errors)


def convert_dataclass_field(
    value,
    field: dataclasses.Field,
    missing_fields: typing.List[str],
    errors: typing.Dict[str, str],
):
    try:
        value = _convert_dataclass_field(value, field)
    except ConvertException as e:
        errors[field.name] = e.errors
    except MissingException:
        missing_fields.append(field.name)
    else:
        return value
    return dataclasses.MISSING


def _convert_dataclass_field(value, field: dataclasses.Field):
    if value is not dataclasses.MISSING:
        return convert(value, field.type)
    if field.default is not dataclasses.MISSING:
        return field.default
    if field.default_factory is not dataclasses.MISSING:
        return field.default_factory()
    elif is_optional(field.type):
        return None
    else:
        raise MissingException


# noinspection PyUnusedLocal
@converter(bool)
def convert_bool(value, type_) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str) and value.lower() in ['true', 'false']:
        return value.lower() == 'true'

    if value == 0:
        return False

    if value == 1:
        return True

    raise ConvertException.cannot_convert(value=value, type_name='bool')


@converter(int)
def convert_int(value, type_) -> int:
    try:
        return type_(value)
    except (TypeError, ValueError):
        raise ConvertException.cannot_convert(value=value, type_name='integer')


@converter(float)
def convert_float(value, type_) -> float:
    try:
        return type_(value)
    except (TypeError, ValueError):
        raise ConvertException.cannot_convert(value=value, type_name='float')


@converter(str)
def convert_str(value, type_) -> str:
    if not isinstance(value, str):
        raise ConvertException.cannot_convert(value=value, type_name='string')
    return type_(value)


@converter(enum.Enum)
def convert_enum(value, type_) -> enum.Enum:
    try:
        return type_(value)
    except ValueError:
        allowed_values = '", "'.join(map(str, (item.value for item in type_)))
        errors = ConvertException.NOT_IN_ALLOWED_VALUES_PATTERN.format(value=value, allowed_values=allowed_values)
        raise ConvertException(errors)


# noinspection PyUnusedLocal
@converter(datetime.date)
def convert_date(value, type_) -> datetime.date:
    try:
        return parser.parse(value).date()
    except (ValueError, TypeError):
        raise ConvertException.cannot_convert(value=value, type_name='date')


# noinspection PyUnusedLocal
@converter(datetime.datetime)
def convert_datetime(value, type_) -> datetime.datetime:
    try:
        return parser.parse(value)
    except (ValueError, TypeError):
        raise ConvertException.cannot_convert(value=value, type_name='datetime')


@converter(list)
def convert_list(value, type_) -> list:
    child_types = getattr(type_, '__args__', [])
    child_type = child_types[0] if child_types else typing.Any

    if not isinstance(value, typing.Iterable):
        raise ConvertException.cannot_convert(value=value, type_name='list')

    updated_value = [
        convert(item, child_type)
        for item in value
    ]
    return updated_value


@converter(set)
def convert_set(value, type_) -> set:
    child_types = getattr(type_, '__args__', [])
    child_type = child_types[0] if child_types else typing.Any

    if not isinstance(value, typing.Iterable):
        raise ConvertException.cannot_convert(value=value, type_name='set')

    try:
        updated_value = {
            convert(item, child_type)
            for item in value
        }
    except TypeError:  # if unhashable type
        raise ConvertException.cannot_convert(value=value, type_name='set')

    return updated_value


@converter(tuple)
def convert_tuple(value, type_) -> tuple:
    child_types = getattr(type_, '__args__', [])
    child_type = child_types[0] if child_types else typing.Any

    if not isinstance(value, typing.Iterable):
        raise ConvertException.cannot_convert(value=value, type_name='list')

    updated_value = tuple(
        convert(item, child_type)
        for item in value
    )
    return updated_value


@converter(dict)
def convert_dict(value, type_) -> dict:
    if not isinstance(value, dict):
        raise ConvertException.cannot_convert(value=value, type_name='object')
    key_and_value_type = getattr(type_, '__args__', None)

    if key_and_value_type is None:
        return value

    # noinspection PyUnresolvedReferences
    if key_and_value_type == typing.Dict.__args__:
        return value

    key_type, value_type = key_and_value_type

    keys = [convert(key, key_type) for key in value.keys()]
    values = [convert(value_, value_type) for value_ in value.values()]
    return dict(zip(keys, values))


@converter(uuid.UUID)
def convert_uuid(value, type_) -> uuid.UUID:
    value = str(value)
    if uuid_regexp.match(value):
        return type_(value)
    raise ConvertException.cannot_convert(value=value, type_name='uuid')


@converter(decimal.Decimal)
def convert_decimal(value, type_) -> decimal.Decimal:
    try:
        return type_(value)
    except (decimal.InvalidOperation, TypeError):
        raise ConvertException.cannot_convert(value=value, type_name='decimal')


# noinspection PyUnusedLocal
@converter(typing.TypeVar)
@converter(type(typing.Any), validator=lambda type_: type_ is typing.Any)
def convert_any(value, type_) -> typing.Any:
    return value
