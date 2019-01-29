import datetime
import decimal
import inspect
import json
import uuid
from enum import Enum
from typing import Callable
from typing import Dict
from typing import Type

from dataclasses import asdict
from dataclasses import is_dataclass

__all__ = (
    'JSONEncoder',
    'register_encoder',
)

_encoder_map: Dict[Type, Callable] = {}


NoneType = type(None)


class EncoderException(Exception):
    pass


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):

        for base_cls in type(obj).mro():
            data = _encoder_map.get(base_cls)
            if data is None:
                continue

            func, need_recursion = data

            try:
                obj = func(obj)
            except EncoderException:
                continue

            return self.default(obj) if need_recursion else obj

        return super().default(obj)


def register_encoder(func: Callable=None, *, need_recursion=False):
    if func is None:
        return lambda func: register_encoder(func, need_recursion=need_recursion)

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
    _encoder_map[annotation] = func, need_recursion


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
def set_encoder(set_: set):
    return list(set_)

@register_encoder(need_recursion=True)
def enum_encoder(enum: Enum):
    return enum.value


@register_encoder
def dataclass_encoder(obj: object):
    if not is_dataclass(obj):
        raise EncoderException
    return asdict(obj)
