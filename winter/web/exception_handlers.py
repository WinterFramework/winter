from functools import cache
from http import HTTPStatus
from typing import Iterable
from typing import Type

from winter.components import Component
from .exceptions import RedirectException
from .exceptions import RequestDataDecodeException
from .exceptions import ThrottleException
from .exceptions import UnsupportedMediaTypeException
from .exceptions.handlers import ExceptionHandlers
from .exceptions.handlers import exception_handler
from .exceptions.handlers import find_handlers
from .exceptions.problem_annotation import ProblemAnnotation
from .exceptions.problem_handling import ProblemExceptionHandlerGenerator
from .exceptions.problem_handling import ProblemExceptionMapper
from .exceptions.problem_handling_info import ProblemHandlingInfo
from .pagination.limits import MaximumLimitValueExceeded
from .response import Response
from .response_header_annotation import ResponseHeader
from .response_header_annotation import response_header
from .response_status_annotation import response_status
from .web_application import WebApplication


class BuiltInExceptionHandlers:
    @exception_handler
    @response_status(HTTPStatus.INTERNAL_SERVER_ERROR)
    def handle(self, exception: Exception) -> Response:
        return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, body=b'Server Error (500)')

    @exception_handler
    @response_status(HTTPStatus.FOUND)
    @response_header('Location', 'location_header')
    def handle_redirect(self, exception: RedirectException, location_header: ResponseHeader[str]):
        location_header.set(exception.redirect_to)


# The exceptions that winter.web itself raises, and the last resort for any other one
_BUILT_IN = (
    BuiltInExceptionHandlers,
    ThrottleException,
    RequestDataDecodeException,
    UnsupportedMediaTypeException,
    MaximumLimitValueExceeded,
)
_problem_handler_generator = ProblemExceptionHandlerGenerator(ProblemExceptionMapper())


def find_exception_handlers(app: WebApplication) -> ExceptionHandlers:
    """
    The exception handlers of an application: the @exception_handler methods and the handlers of the @problem
    exceptions among its definitions, over the built-in ones. A handler of the application replaces the built-in
    handler of the same exception class.
    """
    return ExceptionHandlers({**_handlers_in(_BUILT_IN), **_handlers_in(app.definitions)})


def built_in_exception_handlers() -> ExceptionHandlers:
    return ExceptionHandlers(_handlers_in(_BUILT_IN))


def _handlers_in(definitions: Iterable) -> dict:
    return find_handlers([_problem_handler(definition) or definition for definition in definitions])


def _problem_handler(definition) -> Type | None:
    component = Component.get_all().get(definition)
    problem_annotation = component and component.annotations.get_one_or_none(ProblemAnnotation)
    return problem_annotation and _generate_problem_handler(definition, problem_annotation.handling_info)


@cache
def _generate_problem_handler(exception_class: Type[Exception], handling_info: ProblemHandlingInfo) -> Type:
    return _problem_handler_generator.generate(exception_class, handling_info)
