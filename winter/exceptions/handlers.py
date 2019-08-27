import abc
from typing import Dict
from typing import MutableMapping
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from rest_framework.request import Request

from .throws import get_throws
from .. import arguments_resolver
from ..core import ComponentMethod

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
        assert exception_cls not in self._handlers
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


class MethodExceptionsHandler:
    def __init__(self, method: ComponentMethod):
        super().__init__()
        self._method = method
        self._handlers_by_exception = get_throws(self._method)

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
        return None

    def handle(self, exception: Exception, request: Request, response_headers: MutableMapping[str, str]):
        handler = self.get_handler(exception)
        if handler is None:
            handler = exception_handlers_registry.get_handler(exception)
        return _handle_exception(exception, handler, request, response_headers)


def _handle_exception(exception, handler: Optional[ExceptionHandler], request, response_headers):
    from ..django import convert_result_to_http_response

    if handler is None:
        return None

    handle_method = ComponentMethod.get_or_create(handler.__class__.handle)
    arguments = arguments_resolver.resolve_arguments(handle_method, request, response_headers, {
        'exception': exception,
        'response_headers': response_headers,
    })
    result = handle_method(handler, **arguments)
    return convert_result_to_http_response(request, result, handle_method)


exception_handlers_registry = ExceptionHandlersRegistry()
