import datetime
import decimal
import inspect
import json
import uuid
from enum import Enum
from typing import Callable
from typing import Dict
from typing import Type

__all__ = (
    'JSONEncoder',
    'register_encoder',
)

_encoder_map: Dict[Type, Callable] = {}


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):

        func = _encoder_map.get(type(obj))

        if func is not None:
            return func(obj)

        if isinstance(obj, Enum):
            return self.default(obj.value)

        for type_, func in _encoder_map.items():
            if isinstance(obj, type_):
                return func(obj)

        return super().default(obj)


def register_encoder(func: Callable):
    assert callable(func), 'First argument in register_encoder must be callable'

    signature = inspect.signature(func)
    assert len(signature.parameters), 'Function must have only one argument'
    (parameter_name, parameter), = signature.parameters.items()
    annotation = parameter.annotation
    assert annotation is not parameter.empty, 'First argument in function must have annotation'
    assert inspect.isclass(annotation), 'Annotation must be class'
    assert annotation not in _encoder_map, (
        f'You can not register "{annotation.__name__}" twice. At first unregister it'
    )
    _encoder_map[annotation] = func


@register_encoder
def datetime_encoder(date: datetime.datetime):
    representation = date.isoformat()
    if representation.endswith('+00:00'):
        representation = representation[:-6] + 'Z'
    return representation


@register_encoder
def date_encoder(date: datetime.date):
    return date.isoformat()


@register_encoder
def time_encoder(time: datetime.time):
    if time.utcoffset() is not None:
        raise ValueError("JSON can't represent timezone-aware times.")
    return time.isoformat()


@register_encoder
def timedelta_encoder(timedelta: datetime.timedelta):
    return str(timedelta.total_seconds())


@register_encoder
def decimal_encoder(number: decimal.Decimal):
    return float(number)


@register_encoder
def uuid_encoder(uid: uuid.UUID):
    return str(uid)


@register_encoder
def bytes_encoder(byte: bytes):
    return byte.decode('utf-8')


@register_encoder
def str_encoder(string: str):
    return string


@register_encoder
def int_encoder(number: int):
    return number


@register_encoder
def float_encoder(number: float):
    return number


@register_encoder
def tuple_encoder(array: tuple):
    return array


@register_encoder
def list_encoder(array: list):
    return array


@register_encoder
def set_encoder(array: set):
    return list(array)
