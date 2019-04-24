import abc
import typing
from http import HTTPStatus

from rest_framework.request import Request
from rest_framework.response import Response

from .exceptions import RedirectException
from .throws import get_throws
from ..core import ComponentMethod
from ..core import annotate
from ..response_status import response_status

NotHandled = object()


class ExceptionHandler(abc.ABC):

    def __init__(self):
        handle = self.__class__.handle
        self.handle_method = ComponentMethod.get_or_create(handle)

    @abc.abstractmethod
    def handle(self, request: Request, exception: Exception):  # pragma: no cover
        pass


class RedirectExceptionHandler(ExceptionHandler):
    def handle(self, request: Request, exception: Exception):
        assert isinstance(exception, RedirectException)
        return Response(status=HTTPStatus.FOUND, headers={'Location': exception.redirect_to})


class BadRequestExceptionHandler(ExceptionHandler):
    @response_status(400)
    def handle(self, request: Request, exception: Exception) -> str:
        return str(exception.args[0])  # stupid Exception implementation (Viva Python!)


class ExceptionsHandler(ExceptionHandler):
    HandlersMap = typing.Dict[typing.Type[Exception], ExceptionHandler]

    def __init__(self):
        self._handlers: ExceptionsHandler.HandlersMap = {}
        self._auto_handle_exceptions = set()
        super().__init__()

    @property
    def auto_handle_exception_classes(self) -> typing.Tuple[typing.Type[Exception], ...]:
        return tuple(self._auto_handle_exceptions)

    def add_handler(
            self,
            exception_cls: typing.Type[Exception],
            handler_cls: typing.Type[ExceptionHandler],
            *,
            auto_handle: bool = False,
    ):
        assert exception_cls not in self._handlers
        self._handlers[exception_cls] = handler_cls()

        if auto_handle:
            self._auto_handle_exceptions.add(exception_cls)

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
        if handler is None:
            return NotHandled

        result = handler.handle(request, exception)
        return convert_result_to_http_response(request, result, handler.handle_method)


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
