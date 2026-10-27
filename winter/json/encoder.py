import datetime
import decimal
import enum
import inspect
import json
import types
import uuid
from typing import Callable
from typing import Dict
from typing import Tuple
from typing import Type

import dataclasses

_encoder_map: Dict[Type, Tuple[Callable, bool]] = {}

NoneType = type(None)


class CannotEncode(Exception):
    pass


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        encoders = (_encoder_map.get(base_cls) for base_cls in type(obj).mro())
        encoders = (encoder for encoder in encoders if encoder is not None)

        for func, need_recursion in encoders:
            try:
                obj = func(obj)
            except CannotEncode:
                continue

            return self.default(obj) if need_recursion else obj

        return super().default(obj)


def json_encoder(func: Callable = None, *, need_recursion: bool = False):
    """
    The decorated function encodes the type of its only argument, and its subclasses, as JSON. With need_recursion
    the value it returns is encoded in turn.
    """
    if func is None:
        return lambda func_: json_encoder(func_, need_recursion=need_recursion)

    assert callable(func), 'First argument in json_encoder must be callable'

    signature = inspect.signature(func)
    assert len(signature.parameters), 'Function must have only one argument'
    (parameter_name, parameter), = signature.parameters.items()
    annotation = parameter.annotation
    assert annotation is not parameter.empty, 'First argument in function must have annotation'
    assert inspect.isclass(annotation), 'Annotation must be class'
    assert annotation not in _encoder_map, (
        f'"{annotation.__name__}" already has a JSON encoder'
    )
    _encoder_map[annotation] = func, need_recursion
    return func


@json_encoder
def datetime_encoder(date: datetime.datetime):
    representation = date.isoformat()
    if representation.endswith('+00:00'):
        representation = representation[:-6] + 'Z'
    return representation


@json_encoder
def date_encoder(date: datetime.date):
    return date.isoformat()


@json_encoder
def time_encoder(time: datetime.time):
    if time.utcoffset() is not None:
        raise ValueError("JSON can't represent timezone-aware times.")
    return time.isoformat()


@json_encoder
def timedelta_encoder(timedelta: datetime.timedelta):
    return str(timedelta.total_seconds())


@json_encoder
def decimal_encoder(number: decimal.Decimal):
    return str(number)


@json_encoder
def uuid_encoder(uid: uuid.UUID):
    return str(uid)


@json_encoder
def bytes_encoder(bytes_: bytes):
    return bytes_.decode('utf-8')


@json_encoder
def str_encoder(string: str):
    return string


@json_encoder
def int_encoder(number: int):
    return number


@json_encoder
def float_encoder(number: float):
    return number


@json_encoder
def tuple_encoder(array: tuple):
    return array


@json_encoder
def list_encoder(array: list):
    return array


@json_encoder
def set_encoder(set_: set):
    return list(set_)


@json_encoder
def frozenset_encoder(frozenset_: frozenset):
    return list(frozenset_)


@json_encoder
def generator_encoder(generator: types.GeneratorType):
    return list(generator)


@json_encoder(need_recursion=True)
def enum_encoder(enum_: enum.Enum):
    return enum_.value


@json_encoder
def dataclass_encoder(obj: object):
    if not dataclasses.is_dataclass(obj):
        raise CannotEncode
    return dataclasses.asdict(obj)
