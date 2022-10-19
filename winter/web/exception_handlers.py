from http import HTTPStatus

from .exceptions import ExceptionHandler
from .exceptions import RedirectException
from .response_header_annotation import ResponseHeader
from .response_header_annotation import response_header
from .response_status_annotation import response_status


class RedirectExceptionHandler(ExceptionHandler):
    @response_status(HTTPStatus.FOUND)
    @response_header('Location', 'location_header')
    def handle(self, exception: RedirectException, location_header: ResponseHeader[str]):
        location_header.set(exception.redirect_to)
