from http import HTTPStatus

from dataclasses import dataclass

from .problem import problem


# TODO @response_header.setter('Location', 'redirect_to')
@problem(HTTPStatus.FOUND, auto_handle=True)
@dataclass
class RedirectException(Exception):
    redirect_to: str
