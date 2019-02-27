import dataclasses
from rest_framework.request import Request

import winter


class CustomException(Exception):

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ExceptionWithoutHandler(Exception):
    pass


@dataclasses.dataclass
class CustomExceptionDTO:
    message: str


class CustomExceptionHandler(winter.ExceptionHandler):

    @winter.response_status(400)
    def handle(self, request: Request, exception: CustomException) -> CustomExceptionDTO:
        return CustomExceptionDTO(exception.message)


winter.exceptions_handler.add_handler(CustomException, CustomExceptionHandler)


@winter.controller
@winter.route('controller_with_exceptions/')
class ControllerWithExceptions:

    @winter.route_get('declared_but_not_thrown/')
    @winter.throws(CustomException)
    def declared_but_not_thrown(self) -> str:
        return 'Hello, sir!'

    @winter.route_get('declared_and_thrown/')
    @winter.throws(CustomException)
    def declared_and_thrown(self) -> str:
        raise CustomException('declared_and_thrown')

    @winter.route_get('not_declared_but_thrown/')
    def not_declared_but_thrown(self) -> str:
        raise CustomException('not_declared_but_thrown')

    @winter.route_get('declared_but_no_handler/')
    @winter.throws(ExceptionWithoutHandler)
    def declared_but_no_handler(self) -> str:
        raise ExceptionWithoutHandler()
