import datetime
import decimal
import enum
import inspect
import re
import typing
import uuid

import dataclasses
from dateutil import parser

from winter.type_utils import get_origin_type
from winter.type_utils import is_optional

_decoders = {}

Item = typing.TypeVar('Item')
uuid_regexp = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


class MissingException(Exception):
    pass


class JSONDecodeException(Exception):
    NON_FIELD_ERROR = 'non_field_error'
    MISSING_FIELDS_PATTERN = 'Missing fields: "{missing_fields}"'
    NOT_IN_ALLOWED_VALUES_PATTERN = 'Value not in allowed values("{allowed_values}"): "{value}"'

    def __init__(self, errors: typing.Union[str, typing.Dict]):
        self.errors = errors

    @classmethod
    def invalid_type(cls, value: typing.Any, type_name: typing.Optional[str] = None) -> 'JSONDecodeException':
        if type_name:
            error = 'Invalid type. Need: "{type_name}". Got: "{value}"'.format(value=value, type_name=type_name)
        else:
            error = 'Invalid type.'
        errors = {
            cls.NON_FIELD_ERROR: error,
        }
        return cls(errors)

    @classmethod
    def cannot_decode(cls, value: typing.Any, type_name: str) -> 'JSONDecodeException':
        errors = 'Cannot decode "{value}" to {type_name}'.format(value=value, type_name=type_name)
        return cls(errors)


def json_decoder(type_: typing.Type, validator: typing.Callable = None):
    def wrapper(func):
        decoders = _decoders.setdefault(type_, [])
        decoders.append((func, validator))
        return func

    return wrapper


def json_decode(value, hint_class: typing.Type[Item]) -> Item:
    origin_type = get_origin_type(hint_class)

    types_ = origin_type.mro() if inspect.isclass(origin_type) else type(origin_type).mro()

    for type_ in types_:
        result = _json_decode(value, hint_class, type_)
        if result is not dataclasses.MISSING:
            return result
    raise JSONDecodeException.invalid_type(value)


def _json_decode(value, hint_class: typing.Type[Item], type_: typing.Type) -> typing.Optional[Item]:
    decoders = _decoders.get(type_, [])

    for decoder_, checker in decoders:
        if checker is None or checker(hint_class):
            return decoder_(value, hint_class)
    return dataclasses.MISSING


@json_decoder(object, validator=is_optional)
def decode_optional(value, type_: typing.Type[Item]) -> Item:
    if value is None:
        return None
    type_ = type_.__args__[0]
    return json_decode(value, type_)


@json_decoder(object, validator=dataclasses.is_dataclass)
def decode_dataclass(value: typing.Dict[str, typing.Any], type_: typing.Type[Item]) -> Item:
    if not isinstance(value, typing.Mapping):
        raise JSONDecodeException.invalid_type(value, 'object')

    errors = {}
    decoded_data = {}
    missing_fields = []

    for field in dataclasses.fields(type_):
        field_data = value.get(field.name, dataclasses.MISSING)
        field_data = decode_dataclass_field(field_data, field, missing_fields, errors)
        if field_data is not dataclasses.MISSING:
            decoded_data[field.name] = field_data

    if missing_fields:
        missing_fields = '", "'.join(missing_fields)
        errors[JSONDecodeException.NON_FIELD_ERROR] = JSONDecodeException.MISSING_FIELDS_PATTERN.format(
            missing_fields=missing_fields,
        )
    raise_if_errors(errors)
    return type_(**decoded_data)


def raise_if_errors(errors: typing.Dict[str, str]):
    if errors:
        raise JSONDecodeException(errors)


def decode_dataclass_field(
    value,
    field: dataclasses.Field,
    missing_fields: typing.List[str],
    errors: typing.Dict[str, str],
):
    try:
        value = _decode_dataclass_field(value, field)
    except JSONDecodeException as e:
        errors[field.name] = e.errors
    except MissingException:
        missing_fields.append(field.name)
    else:
        return value
    return dataclasses.MISSING


def _decode_dataclass_field(value, field: dataclasses.Field):
    if value is not dataclasses.MISSING:
        return json_decode(value, field.type)
    if field.default is not dataclasses.MISSING:
        return field.default
    if field.default_factory is not dataclasses.MISSING:
        return field.default_factory()
    elif is_optional(field.type):
        return None
    else:
        raise MissingException


# noinspection PyUnusedLocal
@json_decoder(bool)
def decode_bool(value, type_) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str) and value.lower() in ['true', 'false']:
        return value.lower() == 'true'

    if value == 0:
        return False

    if value == 1:
        return True

    raise JSONDecodeException.cannot_decode(value=value, type_name='bool')


@json_decoder(int)
def decode_int(value, type_) -> int:
    try:
        return type_(value)
    except (TypeError, ValueError):
        raise JSONDecodeException.cannot_decode(value=value, type_name='integer')


@json_decoder(float)
def decode_float(value, type_) -> float:
    try:
        return type_(value)
    except (TypeError, ValueError):
        raise JSONDecodeException.cannot_decode(value=value, type_name='float')


@json_decoder(str)
def decode_str(value, type_) -> str:
    if not isinstance(value, str):
        raise JSONDecodeException.cannot_decode(value=value, type_name='string')
    return type_(value)


@json_decoder(enum.Enum)
def decode_enum(value, type_) -> enum.Enum:
    try:
        return type_(value)
    except ValueError:
        allowed_values = '", "'.join(map(str, (item.value for item in type_)))
        errors = JSONDecodeException.NOT_IN_ALLOWED_VALUES_PATTERN.format(value=value, allowed_values=allowed_values)
        raise JSONDecodeException(errors)


# noinspection PyUnusedLocal
@json_decoder(datetime.date)
def decode_date(value, type_) -> datetime.date:
    try:
        return parser.parse(value).date()
    except (ValueError, TypeError):
        raise JSONDecodeException.cannot_decode(value=value, type_name='date')


# noinspection PyUnusedLocal
@json_decoder(datetime.datetime)
def decode_datetime(value, type_) -> datetime.datetime:
    try:
        return parser.parse(value)
    except (ValueError, TypeError):
        raise JSONDecodeException.cannot_decode(value=value, type_name='datetime')


@json_decoder(list)
def decode_list(value, type_) -> list:
    child_types = getattr(type_, '__args__', [])
    child_type = child_types[0] if child_types else typing.Any

    if not isinstance(value, typing.Iterable):
        raise JSONDecodeException.cannot_decode(value=value, type_name='list')

    updated_value = [
        json_decode(item, child_type)
        for item in value
    ]
    return updated_value


@json_decoder(set)
def decode_set(value, type_) -> set:
    child_types = getattr(type_, '__args__', [])
    child_type = child_types[0] if child_types else typing.Any

    if not isinstance(value, typing.Iterable):
        raise JSONDecodeException.cannot_decode(value=value, type_name='set')

    try:
        updated_value = {
            json_decode(item, child_type)
            for item in value
        }
    except TypeError:  # if unhashable type
        raise JSONDecodeException.cannot_decode(value=value, type_name='set')

    return updated_value


@json_decoder(tuple)
def decode_tuple(value, type_) -> tuple:
    child_types = getattr(type_, '__args__', [])
    child_type = child_types[0] if child_types else typing.Any

    if not isinstance(value, typing.Iterable):
        raise JSONDecodeException.cannot_decode(value=value, type_name='list')

    updated_value = tuple(
        json_decode(item, child_type)
        for item in value
    )
    return updated_value


@json_decoder(dict)
def decode_dict(value, type_) -> dict:
    if not isinstance(value, dict):
        raise JSONDecodeException.cannot_decode(value=value, type_name='object')
    key_and_value_type = getattr(type_, '__args__', None)

    if key_and_value_type is None:
        return value

    # noinspection PyUnresolvedReferences
    if key_and_value_type == typing.Dict.__args__:
        return value

    key_type, value_type = key_and_value_type

    keys = [json_decode(key, key_type) for key in value.keys()]
    values = [json_decode(value_, value_type) for value_ in value.values()]
    return dict(zip(keys, values))


@json_decoder(uuid.UUID)
def decode_uuid(value, type_) -> uuid.UUID:
    value = str(value)
    if uuid_regexp.match(value):
        return type_(value)
    raise JSONDecodeException.cannot_decode(value=value, type_name='uuid')


@json_decoder(decimal.Decimal)
def decode_decimal(value, type_) -> decimal.Decimal:
    try:
        return type_(value)
    except (decimal.InvalidOperation, TypeError):
        raise JSONDecodeException.cannot_decode(value=value, type_name='decimal')


# noinspection PyUnusedLocal
@json_decoder(typing.TypeVar)
@json_decoder(type(typing.Any), validator=lambda type_: type_ is typing.Any)
def decode_any(value, type_) -> typing.Any:
    return value
