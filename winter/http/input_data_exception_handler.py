import typing

from requests import Request

from ..exceptions.handlers import ExceptionHandler
from ..response_status import response_status


class InvalidInputDataException(Exception):

    def __init__(self, errors: typing.Dict[str, str]):
        self.errors = errors


class InvalidInputDataExceptionHandler(ExceptionHandler):
    @response_status(400)
    def handle(self, request: Request, exception: InvalidInputDataException):
        return exception.errors
