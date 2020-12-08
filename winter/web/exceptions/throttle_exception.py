from http import HTTPStatus

from .problem import problem


@problem(status=HTTPStatus.TOO_MANY_REQUESTS, detail='Request was throttled')
class ThrottleException(Exception):
    pass
