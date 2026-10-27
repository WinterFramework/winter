from typing import Type

from dataclasses import dataclass

from winter.components import annotate


@dataclass
class GlobalExceptionAnnotation:
    exception_cls: Type[Exception]


def global_exception(exception_class: Type[Exception]) -> Type[Exception]:
    """The exception may be raised by any API method, so the check of @raises does not require it to be declared."""
    assert issubclass(exception_class, Exception), f'Class "{exception_class}" must be a subclass of Exception'
    annotation = GlobalExceptionAnnotation(exception_cls=exception_class)
    annotation_decorator = annotate(annotation, unique=True)
    annotation_decorator(exception_class)
    return exception_class
