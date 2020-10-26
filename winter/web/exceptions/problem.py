from http import HTTPStatus
from typing import Union

from winter.core import annotate
from .problem_annotation import ProblemAnnotation


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
            status=int(status),
            type=type,
            title=title,
            detail=detail,
            auto_handle=auto_handle,
        )
        annotation_decorator = annotate(annotation, unique=True)
        class_ = annotation_decorator(exception_class)
        return class_
    return wrapper
