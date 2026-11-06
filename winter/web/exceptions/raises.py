from typing import Tuple
from typing import Type

import dataclasses

from winter.components import ComponentMethod
from winter.components import annotate


@dataclasses.dataclass
class ExceptionAnnotation:
    exception_cls: Type[Exception]


def raises(exception_cls: Type[Exception]):
    """
    Declares an exception that the method raises, for its OpenAPI responses. The application must have a handler of
    it other than the one of Exception.
    """
    return annotate(ExceptionAnnotation(exception_cls), unique=True)


def get_raises(method: ComponentMethod) -> Tuple[Type[Exception], ...]:
    return tuple(annotation.exception_cls for annotation in method.annotations.get(ExceptionAnnotation))
