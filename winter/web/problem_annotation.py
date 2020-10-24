from http import HTTPStatus
from typing import Dict
from typing import Type
from typing import Union

from dataclasses import dataclass

from .exceptions import exception_handlers_registry
from ..core import annotate


@dataclass(frozen=True)
class ProblemAnnotation:
    status: HTTPStatus
    title: str
    detail: str
    type: str


def problem(
    status: Union[HTTPStatus, int],
    title: str = '',
    detail: str = '',
    type: str = '',
    auto_handle: bool = False,
):
    def wrapper(exception_class):
        assert issubclass(exception_class, Exception), f'Class "{exception_class}" must be a subclass of Exception'
        annotation = ProblemAnnotation(
            status=status,
            type=type,
            title=title,
            detail=detail,
        )
        if auto_handle:
            _auto_handled_exception_registry[exception_class] = annotation
        annotation_decorator = annotate(annotation, unique=True)
        class_ = annotation_decorator(exception_class)
        return class_
    return wrapper


_auto_handled_exception_registry: Dict[Type[Exception], ProblemAnnotation] = {}


def generate_handlers_for_auto_handled_problem():
    from winter.web.problem_handling import ProblemExceptionMapper
    from winter.web.problem_handling import DefaultExceptionHandlerGenerator

    mapper = ProblemExceptionMapper()
    handler_generator = DefaultExceptionHandlerGenerator()
    for exception_class, problem_annotation in _auto_handled_exception_registry.items():
        handler_class = handler_generator.generate(exception_class, mapper)
        exception_handlers_registry.add_handler(exception_class, handler_class, auto_handle=True)
