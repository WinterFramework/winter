import typing

from requests import Request

from ..exceptions.handlers import ExceptionHandler
from ..response_status import response_status



class InvalidRequestBodyException(Exception):

    def __init__(self, errors_by_fields: typing.Dict[str, str], missing_fields: typing.Iterable[str]):
        self.missing_fields = missing_fields
        self.errors_by_fields = errors_by_fields


class InvalidRequestBodyExceptionHandler(ExceptionHandler):
    NON_FIELD_ERROR = 'non_field_error'
    MISSING_FIELDS_PATTERN = 'Missing fields: {missing_fields}'

    @response_status(400)
    def handle(self, request: Request, exception: InvalidRequestBodyException) -> typing.Dict:
        errors = exception.errors_by_fields
        missing_fields = ", ".join(map(str, exception.missing_fields))
        errors[self.NON_FIELD_ERROR] = self.MISSING_FIELDS_PATTERN.format(missing_fields=missing_fields)
        return errors
