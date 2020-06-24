from typing import List

import dataclasses

from winter.core import annotate_method

ListType = type(List)


@dataclasses.dataclass
class RequestBodyAnnotation:
    argument_name: str


def check_request_body_type(argument_type):
    if not dataclasses.is_dataclass(argument_type) and not isinstance(argument_type, ListType):
        raise AssertionError('Invalid request body type')


def request_body(argument_name: str):

    def wrapper(func_or_method):
        annotation = RequestBodyAnnotation(argument_name)
        annotation_decorator = annotate_method(annotation, single=True)
        method = annotation_decorator(func_or_method)
        argument = method.get_argument(argument_name)
        method_name = method.func.__name__
        assert argument is not None, f'Not found argument "{argument_name}" in "{method_name}"'
        check_request_body_type(argument.type_)
        return method
    return wrapper
