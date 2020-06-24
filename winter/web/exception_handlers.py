from http import HTTPStatus
from typing import Dict

from winter.core.json.decoder import JSONDecodeException
from .exceptions import ExceptionHandler
from .exceptions import ThrottleException
from .response_header_annotation import ResponseHeader
from .response_header_annotation import response_header
from .response_status_annotation import response_status


class DecodeExceptionHandler(ExceptionHandler):
    @response_status(HTTPStatus.BAD_REQUEST)
    def handle(self, exception: JSONDecodeException) -> Dict:
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


class ThrottleExceptionHandler(ExceptionHandler):
    @response_status(HTTPStatus.TOO_MANY_REQUESTS)
    def handle(self, exception: ThrottleException) -> Dict:
        return {
            'detail': 'Request was throttled.',
        }
