import abc
from http import HTTPStatus
from typing import Dict
from typing import Tuple
from typing import Type
from typing import Union

from django.http import HttpResponse

from winter.core import ComponentMethod
from .raises import get_raises

NotHandled = object()


class ExceptionHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self, exception: Exception, **kwargs):  # pragma: no cover
        pass


class DefaultExceptionHandler(ExceptionHandler):
    def handle(self, exception: Exception, **kwargs) -> HttpResponse:
        return HttpResponse(b'Server Error (500)', status=HTTPStatus.INTERNAL_SERVER_ERROR)


class ExceptionHandlersRegistry:
    HandlersMap = Dict[Type[Exception], ExceptionHandler]

    def __init__(self):
        self._handlers: ExceptionHandlersRegistry.HandlersMap = {}
        self._auto_handle_exceptions = set()
        self._default_handler = DefaultExceptionHandler()
        super().__init__()

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
        auto_handled_only: bool = False,
    ) -> ExceptionHandler:
        exception_type = type(exception) if isinstance(exception, Exception) else exception

        for exception_cls, handler in self._handlers.items():
            if issubclass(exception_type, exception_cls) and (
                not auto_handled_only or exception_cls in self._auto_handle_exceptions
            ):
                return handler

        return self._default_handler

    def get_default_handler(self) -> ExceptionHandler:
        return self._default_handler

    def set_default_handler(self, handler_cls: Type[ExceptionHandler]):
        self._default_handler = handler_cls()


class MethodExceptionsManager:
    def __init__(self, method: ComponentMethod):
        super().__init__()
        self._method = method
        self._handlers_by_exception = get_raises(self._method)

    @property
    def declared_exception_classes(self) -> Tuple[Type[Exception], ...]:
        return tuple(self._handlers_by_exception.keys())

    def get_handler(self, exception: Union[Type[Exception], Exception]) -> ExceptionHandler:
        exception_type = type(exception) if isinstance(exception, Exception) else exception

        for exception_cls, handler in self._handlers_by_exception.items():
            if issubclass(exception_type, exception_cls):
                if handler is not None:
                    return handler
                return exception_handlers_registry.get_handler(exception)

        return exception_handlers_registry.get_handler(exception, auto_handled_only=True)


exception_handlers_registry = ExceptionHandlersRegistry()
