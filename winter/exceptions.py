import abc
from collections import defaultdict
from typing import DefaultDict
from typing import Dict
from typing import Optional
from typing import Set
from typing import Type

from rest_framework import status as http_status
from rest_framework.request import Request
from rest_framework.response import Response as HTTPResponse

_throws: DefaultDict[object, Set[Type[Exception]]] = defaultdict(set)


NotHandled = object()


class WinterException(Exception):
    pass


class RedirectException(WinterException):
    def __init__(self, redirect_to: str):
        super().__init__()
        self.redirect_to = redirect_to


def handle_winter_exception(exception: WinterException) -> HTTPResponse:
    if isinstance(exception, RedirectException):
        return HTTPResponse(status=http_status.HTTP_302_FOUND, headers={
            'Location': exception.redirect_to,
        })
    raise exception


class ExceptionHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self, request: Request, exception: Exception):
        pass


def throws(exception_cls: Type[Exception]):
    """Decorator to use on controller methods."""
    def wrapper(func):
        mark_func_throws(func, exception_cls)
        return func
    return wrapper


def mark_func_throws(func, exception_cls: Type[Exception]):
    _throws[func].add(exception_cls)


def get_throws(func) -> Optional[Set[Type[Exception]]]:
    return _throws[func]


def is_expected_to_throw(func, e: Exception) -> bool:
    expected_exception_cls_set = get_throws(func) or set()
    for expected_exception_cls in expected_exception_cls_set:
        if isinstance(e, expected_exception_cls):
            return True
    return False


class ExceptionsHandler(ExceptionHandler):
    HandlersMap = Dict[Type[Exception], Type[ExceptionHandler]]

    def __init__(self):
        self._handlers: ExceptionsHandler.HandlersMap = {}

    def add_handler(self, exception_cls: Type[Exception], handler_cls: Type[ExceptionHandler]):
        assert not self._handlers.get(exception_cls)
        self._handlers[exception_cls] = handler_cls

    def get_handler(self, exception: Exception) -> Optional[ExceptionHandler]:
        for exception_cls, handler_cls in self._handlers.items():
            handler = handler_cls()
            if isinstance(exception, exception_cls):
                return handler
        return None

    def handle(self, request: Request, exception: Exception):
        from .django import convert_result_to_http_response
        handler = self.get_handler(exception)
        if handler:
            result = handler.handle(request, exception)
            return convert_result_to_http_response(request, result, handler.__class__.handle)
        return NotHandled


exceptions_handler = ExceptionsHandler()
