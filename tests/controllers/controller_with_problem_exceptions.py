from http import HTTPStatus
from typing import Dict

import dataclasses

import winter.web
from winter.data.exceptions import NotFoundException


@winter.web.problem(status=HTTPStatus.FORBIDDEN)
class ProblemExistsException(Exception):
    def __str__(self):
        return 'Implicit string of detail'


class InheritorOfProblemExistsException(ProblemExistsException):
    pass


@winter.web.problem(status=HTTPStatus.FORBIDDEN)
@dataclasses.dataclass
class ProblemExistsDataclassException(Exception):
    custom_field: str = 'custom value'

    def __str__(self):
        return 'Implicit string of detail dataclass'


@winter.web.problem(
    status=HTTPStatus.BAD_REQUEST,
    title='All fields problem exists',
    type='urn:problem-type:all-field-problem-exists',
    detail='A lot of interesting things happens with this problem',
)
class AllFieldConstProblemExistsException(Exception):
    pass


class ProblemExistsExceptionHandler(winter.web.ExceptionHandler):
    @winter.response_status(HTTPStatus.FORBIDDEN)
    def handle(self, exception: ProblemExistsException, **kwargs) -> Dict:
        return {'message': str(exception)}


@dataclasses.dataclass
class CustomExceptionDTO:
    message: str


class MyEntity:
    pass


class ProblemExistsExceptionCustomHandler(winter.web.ExceptionHandler):
    @winter.response_status(HTTPStatus.BAD_REQUEST)
    def handle(self, exception: ProblemExistsException) -> CustomExceptionDTO:
        return CustomExceptionDTO(message=str(exception))


@winter.controller
@winter.route('controller_with_problem_exceptions/')
class ControllerWithProblemExceptions:

    @winter.raises(ProblemExistsException)
    @winter.route_get('problem_exists_exception/')
    def problem_exists_exception(self) -> str:
        raise ProblemExistsException()

    @winter.raises(ProblemExistsDataclassException)
    @winter.route_get('problem_exists_dataclass_exception/')
    def problem_exists_dataclass_exception(self) -> str:
        raise ProblemExistsDataclassException()

    @winter.raises(AllFieldConstProblemExistsException)
    @winter.route_get('all_field_const_problem_exists_exception/')
    def all_field_const_problem_exists_exception(self) -> str:
        raise AllFieldConstProblemExistsException()

    @winter.route_get('inherited_problem_exists_exception/')
    def problem_exists_auto_handle_exception(self) -> str:
        raise InheritorOfProblemExistsException()

    @winter.raises(ProblemExistsException, ProblemExistsExceptionCustomHandler)
    @winter.route_get('custom_handler_problem_exists_exception/')
    def custom_handler_problem_exists_exception(self) -> str:
        raise ProblemExistsException()

    @winter.route_get('not_found_exception/')
    def not_found_exception(self) -> str:
        raise NotFoundException(entity_id=1, entity_cls=MyEntity)
