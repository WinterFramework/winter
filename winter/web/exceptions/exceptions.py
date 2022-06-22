from http import HTTPStatus

from .problem import problem


@problem(status=HTTPStatus.TOO_MANY_REQUESTS, detail='Request was throttled')
class ThrottleException(Exception):
    pass


class RedirectException(Exception):
    def __init__(self, redirect_to: str):
        super().__init__()
        self.redirect_to = redirect_to
