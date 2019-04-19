import typing
from typing import Type

import dataclasses

from ..core import ComponentMethod
from ..core import annotate

if typing.TYPE_CHECKING:
    from .handlers import ExceptionHandler


@dataclasses.dataclass
class ExceptionAnnotation:
    exception_cls: typing.Type[Exception]
    handler: typing.Optional['ExceptionHandler'] = None


def throws(exception_cls: Type[Exception], handler_cls: typing.Optional[typing.Type['ExceptionHandler']] = None):
    """Decorator to use on methods."""
    from ..controller import build_controller

    if handler_cls is not None:
        handler = build_controller(handler_cls)
    else:
        handler = None

    return annotate(ExceptionAnnotation(exception_cls, handler), unique=True)


def get_throws(method: ComponentMethod) -> typing.Dict[typing.Type[Exception], 'ExceptionHandler']:
    annotations = method.annotations.get(ExceptionAnnotation)
    return {annotation.exception_cls: annotation.handler for annotation in annotations}
