from typing import Type

import dataclasses

from winter.core import annotate_method


class _BaseResponseHeader:
    pass


class _ResponseHeader:
    def __getitem__(self, value_type: Type):
        assert isinstance(value_type, type), 'value_type must be a type'
        return type(f'ResponseHeader[{value_type.__name__}]', (_BaseResponseHeader,), {})


@dataclasses.dataclass
class ResponseHeaderAnnotation:
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


ResponseHeader = _ResponseHeader()
