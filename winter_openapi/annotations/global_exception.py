from typing import Type

from dataclasses import dataclass

from winter.core import annotate


@dataclass
class GlobalExceptionAnnotation:
    exception_cls: Type[Exception]


def global_exception(exception_class: Type[Exception]) -> Type[Exception]:
    return register_global_exception(exception_class)


def register_global_exception(exception_class: Type[Exception]) -> Type[Exception]:
    assert issubclass(exception_class, Exception), f'Class "{exception_class}" must be a subclass of Exception'
    annotation = GlobalExceptionAnnotation(exception_cls=exception_class)
    annotation_decorator = annotate(annotation, unique=True)
    annotation_decorator(exception_class)
    return exception_class
