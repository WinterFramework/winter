import abc
import typing

from rest_framework.request import Request

from .throws import get_throws
from ..core import ComponentMethod
from ..core import annotate
from ..response_status import response_status

NotHandled = object()


class ExceptionHandler(abc.ABC):
    status_code = None

    def __init__(self):
        handle = self.__class__.handle
        self.handle_method = ComponentMethod.get_or_create(handle)

    @abc.abstractmethod
    def handle(self, request: Request, exception: Exception):  # pragma: no cover
        pass


class BadRequestExceptionHandler(ExceptionHandler):
    @response_status(400)
    def handle(self, request: Request, exception: Exception):
        return str(exception.args[0])  # stupid Exception implementation (Viva Python!)


class ExceptionsHandler(ExceptionHandler):
    HandlersMap = typing.Dict[typing.Type[Exception], ExceptionHandler]

    def __init__(self):
        self._handlers: ExceptionsHandler.HandlersMap = {}
        super().__init__()

    def add_handler(self, exception_cls: typing.Type[Exception], handler_cls: typing.Type[ExceptionHandler]):
        from ..controller import build_controller

        assert exception_cls not in self._handlers
        self._handlers[exception_cls] = build_controller(handler_cls)

    def get_handler(
            self,
            exception: typing.Union[typing.Type[Exception], Exception],
    ) -> typing.Optional[ExceptionHandler]:
        exception_type = type(exception) if isinstance(exception, Exception) else exception

        for exception_cls, handler in self._handlers.items():
            if issubclass(exception_type, exception_cls):
                return handler
        return None

    @annotate(None)
    def handle(self, request: Request, exception: Exception):
        from ..django import convert_result_to_http_response

        handler = self.get_handler(exception)
        if handler is not None:
            result = handler.handle(request, exception)
            return convert_result_to_http_response(request, result, handler.handle_method)
        return NotHandled


class MethodExceptionsHandler(ExceptionHandler):

    def __init__(self, method: ComponentMethod):
        super().__init__()
        self._method = method
        self._handlers_by_exception = get_throws(self._method)

    @property
    def exception_classes(self) -> typing.Tuple[typing.Type[Exception], ...]:
        return tuple(self._handlers_by_exception.keys())

    def get_handler(
            self,
            exception: typing.Union[typing.Type[Exception], Exception],
    ) -> typing.Optional[ExceptionHandler]:
        exception_type = type(exception) if isinstance(exception, Exception) else exception

        for exception_cls, handler in self._handlers_by_exception.items():
            if handler is not None and issubclass(exception_type, exception_cls):
                return handler
        return None

    @annotate(None)
    def handle(self, request: Request, exception: Exception):
        from ..django import convert_result_to_http_response

        handler = self.get_handler(exception)
        if handler is not None:
            result = handler.handle(request, exception)
            return convert_result_to_http_response(request, result, handler.handle_method)
        return exceptions_handler.handle(request, exception)


exceptions_handler = ExceptionsHandler()
