import dataclasses

from winter.core import annotate_method


@dataclasses.dataclass
class RequestBodyAnnotation:
    argument_name: str


def request_body(argument_name: str):

    def wrapper(func_or_method):
        annotation = RequestBodyAnnotation(argument_name)
        annotation_decorator = annotate_method(annotation, single=True)
        method = annotation_decorator(func_or_method)
        argument = method.get_argument(argument_name)
        method_name = method.func.__name__
        assert argument is not None, f'Not found argument "{argument_name}" in "{method_name}"'
        assert dataclasses.is_dataclass(argument.type_), f'Argument should be dataclass in "{method_name}"'
        return method
    return wrapper
