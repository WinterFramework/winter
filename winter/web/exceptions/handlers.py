import abc
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from winter.core import ComponentMethod
from .raises import get_raises

NotHandled = object()


class ExceptionHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self, exception: Exception, **kwargs):  # pragma: no cover
        pass


class ExceptionHandlersRegistry:
    HandlersMap = Dict[Type[Exception], ExceptionHandler]

    def __init__(self):
        self._handlers: ExceptionHandlersRegistry.HandlersMap = {}
        self._auto_handle_exceptions = set()
        super().__init__()

    @property
    def auto_handle_exception_classes(self) -> Tuple[Type[Exception], ...]:
        return tuple(self._auto_handle_exceptions)

    def add_handler(
        self,
        exception_cls: Type[Exception],
        handler_cls: Type[ExceptionHandler],
        *,
        auto_handle: bool = False,
    ):
        assert exception_cls not in self._handlers, exception_cls
        self._handlers[exception_cls] = handler_cls()

        if auto_handle:
            self._auto_handle_exceptions.add(exception_cls)

    def get_handler(
        self,
        exception: Union[Type[Exception], Exception],
    ) -> Optional[ExceptionHandler]:
        exception_type = type(exception) if isinstance(exception, Exception) else exception

        for exception_cls, handler in self._handlers.items():
            if issubclass(exception_type, exception_cls):
                return handler
        return None


class MethodExceptionsManager:
    def __init__(self, method: ComponentMethod):
        super().__init__()
        self._method = method
        self._handlers_by_exception = get_raises(self._method)

    @property
    def declared_exception_classes(self) -> Tuple[Type[Exception], ...]:
        return tuple(self._handlers_by_exception.keys())

    @property
    def exception_classes(self) -> Tuple[Type[Exception], ...]:
        return self.declared_exception_classes + exception_handlers_registry.auto_handle_exception_classes

    def get_handler(self, exception: Union[Type[Exception], Exception]) -> Optional[ExceptionHandler]:
        exception_type = type(exception) if isinstance(exception, Exception) else exception

        for exception_cls, handler in self._handlers_by_exception.items():
            if handler is not None and issubclass(exception_type, exception_cls):
                return handler

        return exception_handlers_registry.get_handler(exception)


exception_handlers_registry = ExceptionHandlersRegistry()
