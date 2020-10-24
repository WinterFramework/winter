from http import HTTPStatus
from typing import Dict

from winter.core.json.decoder import JSONDecodeException
from .exceptions import ExceptionHandler
from .response_status_annotation import response_status


class DecodeExceptionHandler(ExceptionHandler):
    @response_status(HTTPStatus.BAD_REQUEST)
    def handle(self, exception: JSONDecodeException) -> Dict:
        return exception.errors
