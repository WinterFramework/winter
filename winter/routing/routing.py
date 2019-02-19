from typing import Dict
from typing import Optional
from typing import Tuple

from .route_annotation import RouteAnnotation
from ..http import MediaType

_route_annotations: Dict[object, RouteAnnotation] = {}


def route(url_path: str, http_method: Optional[str] = None, produces: Optional[Tuple[MediaType]] = None):
    def wrapper(func):
        register_route(func, url_path, http_method, produces)
        return func
    return wrapper


def route_get(url_path='', produces: Optional[Tuple[MediaType]] = None):
    return route(url_path, 'GET', produces=produces)


def route_post(url_path='', produces: Optional[Tuple[MediaType]] = None):
    return route(url_path, 'POST', produces=produces)


def route_delete(url_path='', produces: Optional[Tuple[MediaType]] = None):
    return route(url_path, 'DELETE', produces=produces)


def route_patch(url_path='', produces: Optional[Tuple[MediaType]] = None):
    return route(url_path, 'PATCH', produces=produces)


def route_put(url_path='', produces: Optional[Tuple[MediaType]] = None):
    return route(url_path, 'PUT', produces=produces)


def register_route(func, url_path: str, http_method: Optional[str], produces: Optional[Tuple[MediaType]]):
    assert func not in _route_annotations, f'{func} is already has a route'
    _route_annotations[func] = RouteAnnotation(url_path, http_method, produces)


def get_route_annotation(func) -> Optional[RouteAnnotation]:
    return _route_annotations.get(func)
