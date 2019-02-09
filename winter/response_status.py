import typing

from .http_method import HTTPMethod

_default_statuses: typing.Dict[typing.Callable, int] = {}
_default_http_method_statuses = {
    HTTPMethod.GET: 200,
    HTTPMethod.POST: 200,
    HTTPMethod.PATCH: 200,
    HTTPMethod.DELETE: 204,
}


def response_status(status: int):
    def wrapper(func):
        _set_default_response_status(func, status)
        return func

    return wrapper


def get_default_response_status(func: typing.Callable) -> typing.Optional[int]:
    return _default_statuses.get(func)


def _set_default_response_status(func, status: int):
    _default_statuses[func] = status
