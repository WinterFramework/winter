import dataclasses

import winter


class CustomException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class WithUnknownArgumentException(Exception):
    pass


class ExceptionWithoutHandler(Exception):
    pass


@dataclasses.dataclass
class CustomExceptionDTO:
    message: str


class CustomExceptionHandler(winter.ExceptionHandler):
    @winter.response_status(400)
    def handle(self, exception: CustomException) -> CustomExceptionDTO:
        return CustomExceptionDTO(exception.message)


class AnotherExceptionHandler(winter.ExceptionHandler):
    @winter.response_status(401)
    def handle(self, exception: CustomException) -> int:
        return 21


class WithUnknownArgumentExceptionHandler(winter.ExceptionHandler):
    @winter.response_status(400)
    def handle(self, exception: CustomException, unknown_argument: int) -> str:
        return 'Bad Request'


winter.exception_handlers_registry.add_handler(CustomException, CustomExceptionHandler)
winter.exception_handlers_registry.add_handler(WithUnknownArgumentException, WithUnknownArgumentExceptionHandler)


class ChildCustomException(CustomException):
    pass


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

    @winter.route_get('declared_and_thrown_child/')
    @winter.throws(CustomException)
    def declared_and_thrown_child(self) -> str:
        raise ChildCustomException('declared_and_thrown_child')

    @winter.route_get('not_declared_but_thrown/')
    def not_declared_but_thrown(self) -> str:
        raise CustomException('not_declared_but_thrown')

    @winter.route_get('declared_but_no_handler/')
    @winter.throws(ExceptionWithoutHandler)
    def declared_but_no_handler(self) -> str:
        raise ExceptionWithoutHandler()

    @winter.throws(CustomException, AnotherExceptionHandler)
    @winter.route_get('exception_with_custom_handler/')
    def with_custom_handler(self) -> str:
        raise CustomException('message')

    @winter.throws(WithUnknownArgumentException)
    @winter.route_get('with_unknown_argument_exception/')
    def with_unknown_argument_handler(self) -> str:
        raise WithUnknownArgumentException()
