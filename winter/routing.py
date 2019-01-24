from typing import Dict
from typing import NamedTuple
from typing import Optional

_routes: Dict[object, 'Route'] = {}


class Route(NamedTuple):
    url_path: str
    http_method: str = None


def route(url_path: str, http_method: str = None):
    def wrapper(func):
        register_route(func, url_path, http_method)
        return func
    return wrapper


def route_get(url_path=''):
    return route(url_path, 'GET')


def route_post(url_path=''):
    return route(url_path, 'POST')


def route_delete(url_path=''):
    return route(url_path, 'DELETE')


def route_patch(url_path=''):
    return route(url_path, 'PATCH')


def register_route(func, url_path, http_method):
    assert func not in _routes, f'{func} is already mapped to a route'
    _routes[func] = Route(url_path, http_method)


def get_function_route(func) -> Optional[Route]:
    return _routes.get(func)
