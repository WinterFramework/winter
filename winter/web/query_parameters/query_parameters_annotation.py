import dataclasses

from winter.core import ComponentMethod
from winter.core import ComponentMethodArgument
from winter.core import annotate_method


@dataclasses.dataclass
class QueryParametersAnnotation:
    argument: ComponentMethodArgument


def query_parameters(argument_name: str):

    def wrapper(func_or_method):
        method = ComponentMethod.get_or_create(func_or_method)
        argument = method.get_argument(argument_name)
        method_name = method.func.__name__
        assert argument is not None, f'Not found argument "{argument_name}" in "{method_name}"'
        annotation = QueryParametersAnnotation(argument)
        annotation_decorator = annotate_method(annotation, single=True)
        method = annotation_decorator(func_or_method)
        return method
    return wrapper
