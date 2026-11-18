import datetime
import enum
from email.utils import format_datetime
from typing import MutableMapping

import dataclasses

from winter.components import annotate_method

_VALUE_TYPES = (str, int, datetime.datetime)


class _ResponseHeaderMeta(type):
    def __getitem__(self, value_type):
        if value_type not in _VALUE_TYPES:
            name = value_type.__qualname__ if isinstance(value_type, type) else repr(value_type)
            raise TypeError(f'{self.__name__}[{name}]: a response header is str, int or datetime')
        return _ResponseHeaderMeta.__new__(
            type(self),
            f'{self.__name__}[{value_type.__name__}]',
            (self, ),
            {
                '_value_type': value_type,
            },

        )


@dataclasses.dataclass
class ResponseHeaderAnnotation:
    # TODO: add inspector for this annotation (https://github.com/mofr/winter/issues/135)
    header_name: str
    argument_name: str


def response_header(header_name: str, argument_name: str):
    def wrapper(func_or_method):
        annotation = ResponseHeaderAnnotation(header_name, argument_name)
        annotation_decorator = annotate_method(annotation)
        method = annotation_decorator(func_or_method)
        argument = method.get_argument(argument_name)
        method_name = method.func.__name__
        assert argument is not None, f'Not found argument "{argument_name}" in "{method_name}"'
        return method
    return wrapper


class ResponseHeader(metaclass=_ResponseHeaderMeta):
    """A header of the response: a str as is, an int as a number, a datetime as an HTTP-date in GMT."""
    _value_type = str

    def __init__(self, headers: MutableMapping[str, str], header_name: str):
        self._headers = headers
        self._header_name = header_name.lower()

    def __repr__(self):
        return f'{self.__class__.__name__}({self._header_name!r})'

    def set(self, value):
        if isinstance(value, enum.Enum):
            raise TypeError(f'{self._header_name}: an enum is set by its value, not {value!r}')
        if isinstance(value, bool) or not isinstance(value, self._value_type):
            raise TypeError(f'{self._header_name}: {value!r} is not {self._value_type.__name__}')
        if isinstance(value, datetime.datetime):
            if value.utcoffset() is None:
                raise ValueError(
                    f'{self._header_name}: a datetime without a time zone has no HTTP-date, give it tzinfo',
                )
            self._headers[self._header_name] = format_datetime(value.astimezone(datetime.timezone.utc), usegmt=True)
        else:
            self._headers[self._header_name] = str(value)
