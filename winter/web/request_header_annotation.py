import dataclasses

from winter.core import annotate_method


@dataclasses.dataclass
class RequestHeaderAnnotation:
    name: str
    map_to: str


def request_header(name: str, *, to: str):

    def wrapper(func_or_method):
        annotation = RequestHeaderAnnotation(name, to)
        annotation_decorator = annotate_method(annotation)
        method = annotation_decorator(func_or_method)
        argument = method.get_argument(to)
        method_name = method.func.__name__
        assert argument is not None, f'Not found argument "{to}" in "{method_name}"'
        return method

    return wrapper
