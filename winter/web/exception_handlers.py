from functools import cache
from http import HTTPStatus
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import Optional
from typing import Type

from winter.components import Component
from winter.components import ComponentMethod
from .exceptions import RedirectException
from .exceptions.handlers import exception_handler
from .exceptions.handlers import find_handlers
from .exceptions.problem_annotation import ProblemAnnotation
from .exceptions.problem_handling import ProblemExceptionHandlerGenerator
from .exceptions.problem_handling import ProblemExceptionMapper
from .exceptions.problem_handling_info import ProblemHandlingInfo
from .exceptions.raises import get_raises
from .response_header_annotation import ResponseHeader
from .response_header_annotation import response_header
from .response_status_annotation import response_status
from .routing import Route
from .web_application import WebApplication


class BuiltInExceptionHandlers:
    @exception_handler
    @response_status(HTTPStatus.FOUND)
    @response_header('Location', 'location_header')
    def handle_redirect(self, exception: RedirectException, location_header: ResponseHeader[str]):
        location_header.set(exception.redirect_to)


class ExceptionHandlers:
    """
    The exception handlers of an application. The nearest class in the MRO of an exception that has a handler, of the
    application or a built-in one, or that is a @problem exception, handles it. An exception that none handles goes to
    the host, such as Django or a WSGI server, which logs it and answers 500.
    """

    def __init__(self, handlers: Dict[Type[Exception], ComponentMethod]):
        self._handlers = handlers

    def get(self, exception_cls: Type[Exception]) -> Optional[ComponentMethod]:
        handled_cls = self._nearest_handled_class(exception_cls)
        return self._handler_of(handled_cls) if handled_cls is not None else None

    def has_specific_handler(self, exception_cls: Type[Exception]) -> bool:
        """Whether a handler of the exception class or of a base class other than Exception handles it."""
        return self._nearest_handled_class(exception_cls) not in (None, Exception)

    def _nearest_handled_class(self, exception_cls: Type[Exception]) -> Optional[Type[Exception]]:
        return next((cls for cls in exception_cls.__mro__ if self._handler_of(cls) is not None), None)

    def _handler_of(self, cls: type) -> Optional[ComponentMethod]:
        return self._handlers[cls] if cls in self._handlers else _problem_handler(cls)

    def __iter__(self) -> Iterator[ComponentMethod]:
        """Each handler of the application and built-in one once, also the one of several exceptions."""
        return iter(dict.fromkeys(self._handlers.values()))


def find_exception_handlers(app: WebApplication) -> ExceptionHandlers:
    """
    The exception handlers of an application: the @exception_handler methods among its definitions over the built-in
    ones. A handler of the application replaces the built-in one, or the one of @problem, of the same exception class.
    """
    return ExceptionHandlers({**find_handlers([BuiltInExceptionHandlers]), **find_handlers(app.definitions)})


def check_raises(routes: Iterable[Route], exception_handlers: ExceptionHandlers):
    """Fails on startup for an exception declared with @raises that no handler handles but the one of Exception."""
    for route in routes:
        for exception_cls in get_raises(route.method):
            if not exception_handlers.has_specific_handler(exception_cls):
                raise ValueError(
                    f'{exception_cls.__name__} is declared with @raises in {route.method.full_name} '
                    f'and has no handler in the application',
                )


def built_in_exception_handlers() -> ExceptionHandlers:
    return ExceptionHandlers(find_handlers([BuiltInExceptionHandlers]))


_problem_handler_generator = ProblemExceptionHandlerGenerator(ProblemExceptionMapper())


def _problem_handler(cls: type) -> Optional[ComponentMethod]:
    component = Component.get_all().get(cls)
    problem_annotation = component and component.annotations.get_one_or_none(ProblemAnnotation)
    return problem_annotation and _generate_problem_handler(cls, problem_annotation.handling_info)


@cache
def _generate_problem_handler(exception_class: Type[Exception], handling_info: ProblemHandlingInfo) -> ComponentMethod:
    handler_class = _problem_handler_generator.generate(exception_class, handling_info)
    return find_handlers([handler_class])[exception_class]
