from http import HTTPStatus

from .problem import problem


@problem(status=HTTPStatus.TOO_MANY_REQUESTS, detail='Request was throttled', auto_handle=True)
class ThrottleException(Exception):
    pass
