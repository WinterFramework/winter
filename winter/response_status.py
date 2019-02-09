import typing

from .http_method import HttpMethod

_default_statuses: typing.Dict[typing.Callable, int] = {}
_default_http_method_statuses = {
    HttpMethod.GET: 200,
    HttpMethod.POST: 200,
    HttpMethod.PATCH: 200,
    HttpMethod.DELETE: 204,
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
