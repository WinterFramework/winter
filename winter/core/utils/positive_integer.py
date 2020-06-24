from ..json import JSONDecodeException
from ..json import json_decoder


class PositiveInteger(int):

    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):
        if self < 0:
            raise ValueError(f'PositiveInteger can not be negative: {self}')
        super().__init__()


@json_decoder(PositiveInteger)
def decode_positive_integer(value, type_):
    try:
        return type_(value)
    except (TypeError, ValueError):
        raise JSONDecodeException.cannot_decode(value=value, type_name='PositiveInteger')
