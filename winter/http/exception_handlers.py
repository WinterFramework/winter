import typing
from http import HTTPStatus

from .response_header_annotation import ResponseHeader
from .response_header_annotation import response_header
from .response_status_annotation import response_status
from .. import ExceptionHandler
from ..converters import ConvertException


class ConvertExceptionHandler(ExceptionHandler):
    @response_status(HTTPStatus.BAD_REQUEST)
    def handle(self, exception: ConvertException) -> typing.Dict:
        return exception.errors


class RedirectExceptionHandler(ExceptionHandler):
    @response_status(HTTPStatus.FOUND)
    @response_header('Location', 'location_header')
    def handle(self, exception: Exception, location_header: ResponseHeader[str]):
        location_header.set(exception.redirect_to)


class BadRequestExceptionHandler(ExceptionHandler):
    @response_status(HTTPStatus.BAD_REQUEST)
    def handle(self, exception: Exception) -> str:
        return str(exception.args[0])  # stupid Exception implementation (Viva Python!)
