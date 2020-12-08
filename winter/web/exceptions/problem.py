from http import HTTPStatus
from typing import Optional
from typing import Union

from winter.core import annotate
from .problem_annotation import ProblemAnnotation
from .problem_handling_info import ProblemHandlingInfo


def problem(
    status: Union[HTTPStatus, int],
    title: Optional[str] = None,
    detail: Optional[str] = None,
    type: Optional[str] = None,
):
    def wrapper(exception_class):
        assert issubclass(exception_class, Exception), f'Class "{exception_class}" must be a subclass of Exception'
        annotation = ProblemAnnotation(
            handling_info=ProblemHandlingInfo(
                status=int(status),
                type=type,
                title=title,
                detail=detail,
            ),
        )
        annotation_decorator = annotate(annotation, unique=True)
        class_ = annotation_decorator(exception_class)
        return class_
    return wrapper
