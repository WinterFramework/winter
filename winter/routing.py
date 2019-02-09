import typing

import dataclasses

from .http_method import HttpMethod

_routes: typing.Dict[typing.Callable, 'Route'] = {}


@dataclasses.dataclass(frozen=True)
class Route:
    url_path: str
    http_method: HttpMethod = None


def route(url_path: str, http_method: HttpMethod = None):
    def wrapper(func):
        register_route(func, url_path, http_method)
        return func

    return wrapper


def route_get(url_path=''):
    return route(url_path, HttpMethod.GET)


def route_post(url_path=''):
    return route(url_path, HttpMethod.POST)


def route_delete(url_path=''):
    return route(url_path, HttpMethod.DELETE)


def route_patch(url_path=''):
    return route(url_path, HttpMethod.PATCH)


def route_put(url_path=''):
    return route(url_path, HttpMethod.PUT)


def register_route(func, url_path, http_method):
    assert func not in _routes, f'{func} is already mapped to a route'
    _routes[func] = Route(url_path, http_method)


def get_route(func: typing.Union[type, typing.Callable]) -> typing.Optional[Route]:
    return _routes.get(func)
