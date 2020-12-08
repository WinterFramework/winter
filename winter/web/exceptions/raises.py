from typing import Dict
from typing import Optional
from typing import TYPE_CHECKING
from typing import Type

import dataclasses

from winter.core import ComponentMethod
from winter.core import annotate

if TYPE_CHECKING:
    from .handlers import ExceptionHandler  # noqa: F401


@dataclasses.dataclass
class ExceptionAnnotation:
    exception_cls: Type[Exception]
    handler: Optional['ExceptionHandler'] = None


def raises(exception_cls: Type[Exception], handler_cls: Optional[Type['ExceptionHandler']] = None):
    """Decorator to use on methods."""
    if handler_cls is not None:
        handler = handler_cls()
    else:
        handler = None

    return annotate(ExceptionAnnotation(exception_cls, handler), unique=True)


def get_raises(method: ComponentMethod) -> Dict[Type[Exception], 'ExceptionHandler']:
    annotations = method.annotations.get(ExceptionAnnotation)
    return {annotation.exception_cls: annotation.handler for annotation in annotations}
