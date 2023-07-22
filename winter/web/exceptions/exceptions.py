import dataclasses
from http import HTTPStatus
from typing import Dict
from typing import Optional
from typing import Union

from .problem import problem


@problem(status=HTTPStatus.TOO_MANY_REQUESTS, detail='Request was throttled')
class ThrottleException(Exception):
    pass


class RedirectException(Exception):
    def __init__(self, redirect_to: str):
        super().__init__()
        self.redirect_to = redirect_to


@problem(status=HTTPStatus.BAD_REQUEST)
@dataclasses.dataclass
class RequestDataDecodeException(Exception):
    errors: Dict = dataclasses.field(default_factory=dict)

    def __init__(self, errors: Optional[Union[str, Dict]]):
        super().__init__('Failed to decode request data')
        if type(errors) == dict:
            self.errors = errors
        else:
            self.errors = {'error': errors}


@problem(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
class UnsupportedMediaTypeException(Exception):
    pass
