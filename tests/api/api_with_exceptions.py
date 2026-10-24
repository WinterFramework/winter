import dataclasses

import winter.web
from winter.web import route_get, route, raises, response_status


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


class ExceptionHandlers:
    @winter.web.exception_handler
    @response_status(400)
    def handle_custom(self, exception: CustomException) -> CustomExceptionDTO:
        return CustomExceptionDTO(exception.message)

    @winter.web.exception_handler
    @response_status(400)
    def handle_with_unknown_argument(
        self,
        exception: WithUnknownArgumentException,
        unknown_argument: int,
    ) -> str:  # pragma: no cover
        pass


class ChildCustomException(CustomException):
    pass


@route('with_exceptions/')
class APIWithExceptions:

    @route_get('declared_but_not_thrown/')
    @raises(CustomException)
    def declared_but_not_thrown(self) -> str:
        return 'Hello, sir!'

    @route_get('declared_and_thrown/')
    @raises(CustomException)
    def declared_and_thrown(self) -> str:
        raise CustomException('declared_and_thrown')

    @route_get('declared_and_thrown_child/')
    @raises(CustomException)
    def declared_and_thrown_child(self) -> str:
        raise ChildCustomException('declared_and_thrown_child')

    @route_get('not_declared_but_thrown/')
    def not_declared_but_thrown(self) -> str:
        raise CustomException('not_declared_but_thrown')

    @route_get('declared_but_no_handler/')
    @raises(ExceptionWithoutHandler)
    def declared_but_no_handler(self) -> str:
        raise ExceptionWithoutHandler()

    @raises(WithUnknownArgumentException)
    @raises(CustomException)  # second "raises" just for 100% test coverage
    @route_get('with_unknown_argument_exception/')
    def with_unknown_argument_handler(self) -> str:
        raise WithUnknownArgumentException()
