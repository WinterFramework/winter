import typing
from types import FunctionType
from typing import Dict
from typing import NamedTuple
from typing import Optional

import uritemplate

from .urls import get_regexp

_routes: Dict[object, 'Route'] = {}


class Route(NamedTuple):
    url_path: str
    func: typing.Iterable[FunctionType] = None
    http_method: str = None

    @property
    def url(self):
        return rewrite_uritemplate_with_regexps(self.url_path, [self.func])


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


def route_put(url_path=''):
    return route(url_path, 'PUT')


def register_route(func, url_path, http_method):
    assert func not in _routes, f'{func} is already mapped to a route'
    _routes[func] = Route(url_path, func, http_method)


def get_function_route(func) -> Optional[Route]:
    return _routes.get(func)


def rewrite_uritemplate_with_regexps(winter_url_path: str, methods: typing.List) -> str:
    url_path = winter_url_path
    for variable_name in uritemplate.variables(winter_url_path):
        types = {typing.get_type_hints(method).get(variable_name) for method in methods} or {None}
        if len(types) > 1:
            raise Exception(
                f'Different methods are bound to the same path variable, but have different types annotated: {types}'
            )
        type_, = types
        regexp = get_regexp(type_)
        url_path = url_path.replace(f'{{{variable_name}}}', f'(?P<{variable_name}>{regexp})')
    return url_path
