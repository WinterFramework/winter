import inspect
from dataclasses import dataclass
from typing import Dict
from typing import Iterable
from typing import Tuple
from typing import Type

from winter.components import Component
from winter.components import ComponentMethod
from winter.components import annotate_method
from winter.typing import get_union_args
from winter.typing import is_union


@dataclass(frozen=True)
class ExceptionHandlerAnnotation:
    pass


def exception_handler(method):
    """
    Marks a method as an exception handler. It handles the exceptions its first argument is annotated with,
    `UploadError | DownloadError` for several, in the applications whose definitions include its class.
    """
    return annotate_method(ExceptionHandlerAnnotation(), single=True)(method)


class ExceptionHandlers:
    """The exception handlers of an application. The handler of the nearest class in its MRO handles an exception."""

    def __init__(self, handlers: Dict[Type[Exception], ComponentMethod]):
        assert Exception in handlers, 'Every exception must have a handler'
        self._handlers = dict(handlers)

    def get(self, exception_cls: Type[Exception]) -> ComponentMethod:
        return next(self._handlers[cls] for cls in exception_cls.__mro__ if cls in self._handlers)


def find_handlers(classes: Iterable[type]) -> Dict[Type[Exception], ComponentMethod]:
    """The handlers marked with @exception_handler in the classes, by the exception they handle."""
    handlers: Dict[Type[Exception], ComponentMethod] = {}
    components = Component.get_all()
    for cls in classes:
        component = components.get(cls)
        methods = component.methods if component is not None else ()
        for method in methods:
            if method.annotations.get_one_or_none(ExceptionHandlerAnnotation) is None:
                continue
            for exception_cls in handled_exceptions(method):
                if exception_cls in handlers:
                    raise ValueError(
                        f'{exception_cls.__name__} has two handlers: {handlers[exception_cls].full_name} '
                        f'and {method.full_name}',
                    )
                handlers[exception_cls] = method
    return handlers


def handled_exceptions(method: ComponentMethod) -> Tuple[Type[Exception], ...]:
    argument = method.get_argument(exception_argument_name(method))
    type_ = argument.type_ if argument is not None else None
    exception_classes = tuple(get_union_args(type_)) if is_union(type_) else (type_,)
    if not all(inspect.isclass(cls) and issubclass(cls, Exception) for cls in exception_classes):
        raise TypeError(
            f'{method.full_name}: the first argument of an exception handler must be annotated '
            f'with the exceptions it handles',
        )
    return exception_classes


def exception_argument_name(method: ComponentMethod) -> str:
    """The name of the argument that receives the exception: the first one after self."""
    parameters = list(method.signature.parameters)
    return parameters[1] if len(parameters) > 1 else ''
