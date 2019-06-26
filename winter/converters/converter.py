import typing

Dataclass = typing.TypeVar('Dataclass')

class Exc(Exception):
    pass


def convert(data: typing.Dict[str, typing.Any], type_: typing.Type[Dataclass]) -> Dataclass:
    pass

_converters = {}

def converter(type_: typing.Type):
    assert type_ not in _converters

    def wrapper(func):
        _converters[type_] = func
        return func

    return wrapper


@converter(int)
def int_converter(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        raise