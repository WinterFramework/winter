import typing

from rest_framework.request import Request

from .converter import ConvertException
from ..exceptions.handlers import ExceptionHandler
from ..response_status import response_status


class ConvertExceptionHandler(ExceptionHandler):

    @response_status(400)
    def handle(self, request: Request, exception: ConvertException) -> typing.Dict:
        return exception.errors
