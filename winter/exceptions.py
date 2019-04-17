import abc
import typing
from collections import defaultdict
from typing import DefaultDict
from typing import Dict
from typing import Optional
from typing import Set
from typing import Type

import dataclasses
from rest_framework import status as http_status
from rest_framework.request import Request
from rest_framework.response import Response as HTTPResponse

from .core import ComponentMethod
from .core import annotate

_throws: DefaultDict[object, Set[Type[Exception]]] = defaultdict(set)

NotHandled = object()


@dataclasses.dataclass
class ExceptionAnnotation:
    exception_cls: typing.Type[Exception]
    handler: typing.Optional['ExceptionHandler'] = None


class WinterException(Exception):
    pass


class RedirectException(WinterException):

    def __init__(self, redirect_to: str):
        super().__init__()
        self.redirect_to = redirect_to


def handle_winter_exception(exception: WinterException) -> HTTPResponse:
    if isinstance(exception, RedirectException):
        return HTTPResponse(
            status=http_status.HTTP_302_FOUND, headers={
                'Location': exception.redirect_to,
            }
        )
    raise exception


class ExceptionHandler(abc.ABC):
    status_code = None

    def __init__(self):
        handle = self.__class__.handle
        self.handle_method = ComponentMethod.get_or_create(handle)

    @abc.abstractmethod
    def handle(self, request: Request, exception: Exception):  # pragma: no cover
        pass


def throws(exception_cls: Type[Exception], handler_cls: typing.Optional[typing.Type[ExceptionHandler]] = None):
    """Decorator to use on methods."""
    from .controller import build_controller

    if handler_cls is not None:
        handler = build_controller(handler_cls)
    else:
        handler = None

    return annotate(ExceptionAnnotation(exception_cls, handler), unique=True)


def get_throws(method: ComponentMethod) -> typing.Dict[typing.Type[Exception], ExceptionHandler]:
    annotations = method.annotations.get(ExceptionAnnotation)
    return {annotation.exception_cls: annotation.handler for annotation in annotations}


class ExceptionsHandler(ExceptionHandler):
    HandlersMap = Dict[Type[Exception], ExceptionHandler]

    def __init__(self):
        self._handlers: ExceptionsHandler.HandlersMap = {}
        super().__init__()

    def add_handler(self, exception_cls: Type[Exception], handler_cls: Type[ExceptionHandler]):
        from .controller import build_controller

        assert exception_cls not in self._handlers
        self._handlers[exception_cls] = build_controller(handler_cls)

    def get_handler(self, exception: typing.Union[typing.Type[Exception], Exception]) -> Optional[ExceptionHandler]:
        exception_type = type(exception) if isinstance(exception, Exception) else exception

        for exception_cls, handler in self._handlers.items():
            if issubclass(exception_type, exception_cls):
                return handler
        return None

    @annotate(None)
    def handle(self, request: Request, exception: Exception):
        from .django import convert_result_to_http_response

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
    def exception_classes(self) -> typing.Tuple[Type[Exception], ...]:
        return tuple(self._handlers_by_exception.keys())

    def get_handler(self, exception: typing.Union[typing.Type[Exception], Exception]) -> Optional[ExceptionHandler]:
        exception_type = type(exception) if isinstance(exception, Exception) else exception

        for exception_cls, handler in self._handlers_by_exception.items():
            if handler is not None and issubclass(exception_type, exception_cls):
                return handler
        return None

    @annotate(None)
    def handle(self, request: Request, exception: Exception):
        from .django import convert_result_to_http_response

        handler = self.get_handler(exception)
        if handler is not None:
            result = handler.handle(request, exception)
            return convert_result_to_http_response(request, result, handler.handle_method)
        return exceptions_handler.handle(request, exception)


exceptions_handler = ExceptionsHandler()
