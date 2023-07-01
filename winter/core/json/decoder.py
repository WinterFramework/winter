import dataclasses
import datetime
import decimal
import enum
import inspect
import re
import uuid
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from dateutil import parser

from winter.core.utils.typing import get_generic_args
from winter.core.utils.typing import get_origin_type
from winter.core.utils.typing import get_union_args
from winter.core.utils.typing import is_optional
from winter.core.utils.typing import is_union
from .undefined import Undefined

try:
    from collections.abc import Sequence
except ImportError:  # pragma: no cover
    from collections import Sequence  # Old import for versions older than Python3.10

_decoders = {}

Item = TypeVar('Item')
uuid_regexp = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z')


class _MissingException(Exception):
    pass


class JSONDecodeException(Exception):
    NON_FIELD_ERROR = 'non_field_error'

    def __init__(self, errors: Union[str, Dict]):
        self.errors = errors

    @classmethod
    def invalid_type(cls, value: Any, type_name: Optional[str] = None) -> 'JSONDecodeException':
        if type_name:
            error = 'Invalid type. Need: "{type_name}". Got: "{value}"'.format(value=value, type_name=type_name)
        else:
            error = 'Invalid type.'
        errors = {
            cls.NON_FIELD_ERROR: error,
        }
        return cls(errors)

    @classmethod
    def cannot_decode(cls, value: Any, type_name: str) -> 'JSONDecodeException':
        errors = 'Cannot decode "{value}" to {type_name}'.format(value=value, type_name=type_name)
        return cls(errors)


def json_decoder(type_: Type, validator: Callable = None):
    def wrapper(func):
        decoders = _decoders.setdefault(type_, [])
        decoders.append((func, validator))
        return func

    return wrapper


def json_decode(value, hint_class: Type[Item]) -> Item:
    origin_type = get_origin_type(hint_class)

    types_ = origin_type.mro() if inspect.isclass(origin_type) else type(origin_type).mro()

    for type_ in types_:
        result = _json_decode(value, hint_class, type_)
        if result is not dataclasses.MISSING:
            return result
    raise JSONDecodeException.invalid_type(value)


def _json_decode(value, hint_class: Type[Item], type_: Type) -> Optional[Item]:
    decoders = _decoders.get(type_, [])

    for decoder_, checker in decoders:
        if checker is None or checker(hint_class):
            return decoder_(value, hint_class)
    return dataclasses.MISSING


@json_decoder(object, validator=is_optional)
def decode_optional(value, type_: Type[Item]) -> Item:
    if value is None:
        return None
    type_ = type_.__args__[0]
    return json_decode(value, type_)


def can_be_undefined(type_):
    return is_union(type_) and Undefined in get_union_args(type_)


@json_decoder(object, validator=can_be_undefined)
def decode_undefined(value, type_: Type[Item]) -> Item:
    union_args = get_union_args(type_)
    assert len(union_args) == 2, 'Union with Undefined must have 2 args'
    value_type = union_args[0] if union_args[0] is not Undefined else union_args[1]
    return json_decode(value, value_type)


@json_decoder(object, validator=dataclasses.is_dataclass)
def decode_dataclass(value: Dict[str, Any], type_: Type[Item]) -> Item:
    if not isinstance(value, Mapping):
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
        errors[JSONDecodeException.NON_FIELD_ERROR] = f'Missing fields: "{missing_fields}"'
    raise_if_errors(errors)
    return type_(**decoded_data)


def raise_if_errors(errors: Dict[str, str]):
    if errors:
        raise JSONDecodeException(errors)


def decode_dataclass_field(
    value,
    field: dataclasses.Field,
    missing_fields: List[str],
    errors: Dict[str, str],
):
    try:
        value = _decode_dataclass_field(value, field)
    except JSONDecodeException as e:
        errors[field.name] = e.errors
    except _MissingException:
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
    elif can_be_undefined(field.type):
        return Undefined()
    else:
        raise _MissingException


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
        errors = 'Value not in allowed values("{allowed_values}"): "{value}"'.format(
            value=value,
            allowed_values=allowed_values,
        )
        raise JSONDecodeException(errors)


@json_decoder(enum.IntEnum)
def decode_int_enum(value, type_) -> enum.IntEnum:
    try:
        return type_(int(value))
    except ValueError:
        allowed_values = '", "'.join(map(str, (item.value for item in type_)))
        errors = 'Value not in allowed values("{allowed_values}"): "{value}"'.format(
            value=value,
            allowed_values=allowed_values,
        )
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
@json_decoder(Sequence)
def decode_list(value, type_) -> list:
    child_types = getattr(type_, '__args__', [])
    child_type = child_types[0] if child_types else Any

    if not isinstance(value, Iterable):
        raise JSONDecodeException.cannot_decode(value=value, type_name='list')

    updated_value = [
        json_decode(item, child_type)
        for item in value
    ]
    return updated_value


@json_decoder(set)
def decode_set(value, type_) -> set:
    child_types = getattr(type_, '__args__', [])
    child_type = child_types[0] if child_types else Any

    if not isinstance(value, Iterable):
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
    child_type = child_types[0] if child_types else Any

    if not isinstance(value, Iterable):
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
    key_and_value_type = get_generic_args(type_)

    if not key_and_value_type:
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
@json_decoder(TypeVar)
@json_decoder(type(Any), validator=lambda type_: type_ is Any)
def decode_any(value, type_) -> Any:
    return value
