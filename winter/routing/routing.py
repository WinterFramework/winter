from typing import Dict
from typing import Optional
from typing import Tuple

from dataclasses import dataclass

from ..http import MediaType

_routes: Dict[object, 'Route'] = {}


@dataclass(frozen=True)
class Route:
    url_path: str
    http_method: str = None
    produces: Tuple[MediaType] = ()  # It's used for swagger only at the moment, but will be used in routing later
    consumes: Tuple[MediaType] = ()  # It's used for swagger only at the moment, but will be used in routing later


def route(
        url_path: str,
        http_method: Optional[str] = None,
        produces: Optional[Tuple[MediaType]] = (),
        consumes: Optional[Tuple[MediaType]] = (),
):
    def wrapper(func):
        register_route(func, url_path, http_method, produces, consumes)
        return func
    return wrapper


def route_get(url_path='', produces: Optional[Tuple[MediaType]] = (), consumes: Optional[Tuple[MediaType]] = ()):
    return route(url_path, 'GET', produces=produces, consumes=consumes)


def route_post(url_path='', produces: Optional[Tuple[MediaType]] = (), consumes: Optional[Tuple[MediaType]] = ()):
    return route(url_path, 'POST', produces=produces, consumes=consumes)


def route_delete(url_path='', produces: Optional[Tuple[MediaType]] = (), consumes: Optional[Tuple[MediaType]] = ()):
    return route(url_path, 'DELETE', produces=produces, consumes=consumes)


def route_patch(url_path='', produces: Optional[Tuple[MediaType]] = (), consumes: Optional[Tuple[MediaType]] = ()):
    return route(url_path, 'PATCH', produces=produces, consumes=consumes)


def route_put(url_path='', produces: Optional[Tuple[MediaType]] = (), consumes: Optional[Tuple[MediaType]] = ()):
    return route(url_path, 'PUT', produces=produces, consumes=consumes)


def register_route(
        func,
        url_path: str,
        http_method: Optional[str],
        produces: Optional[Tuple[MediaType]],
        consumes: Optional[Tuple[MediaType]],
):
    assert func not in _routes, f'{func} is already mapped to a route'
    _routes[func] = Route(url_path, http_method, produces, consumes)


def get_function_route(func) -> Optional[Route]:
    return _routes.get(func)
