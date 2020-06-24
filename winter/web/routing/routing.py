from typing import Optional
from typing import Tuple

from winter.core import ComponentMethod
from winter.core import annotate
from .route_annotation import RouteAnnotation
from ..media_type import MediaType
from ..routing.route import Route


def route(
        url_path: str,
        http_method: Optional[str] = None,
        produces: Optional[Tuple[MediaType]] = None,
        consumes: Optional[Tuple[MediaType]] = None,
):
    route_annotation = RouteAnnotation(url_path, http_method, produces, consumes)
    return annotate(route_annotation, single=True)


def route_get(url_path='', produces: Optional[Tuple[MediaType]] = None, consumes: Optional[Tuple[MediaType]] = None):
    return route(url_path, 'GET', produces=produces, consumes=consumes)


def route_post(url_path='', produces: Optional[Tuple[MediaType]] = None, consumes: Optional[Tuple[MediaType]] = None):
    return route(url_path, 'POST', produces=produces, consumes=consumes)


def route_delete(url_path='', produces: Optional[Tuple[MediaType]] = None, consumes: Optional[Tuple[MediaType]] = None):
    return route(url_path, 'DELETE', produces=produces, consumes=consumes)


def route_patch(url_path='', produces: Optional[Tuple[MediaType]] = None, consumes: Optional[Tuple[MediaType]] = None):
    return route(url_path, 'PATCH', produces=produces, consumes=consumes)


def route_put(url_path='', produces: Optional[Tuple[MediaType]] = None, consumes: Optional[Tuple[MediaType]] = None):
    return route(url_path, 'PUT', produces=produces, consumes=consumes)


def get_route(method: ComponentMethod) -> Optional[Route]:
    route_annotation = method.annotations.get_one_or_none(RouteAnnotation)
    if route_annotation is None:
        return None

    url_path = get_url_path(method)
    route = Route(
        route_annotation.http_method,
        url_path,
        method,
    )
    return route


def get_url_path(method: ComponentMethod) -> str:
    if method.component is None:
        component_route_annotation = None
    else:
        route_annotations = method.component.annotations
        component_route_annotation = route_annotations.get_one_or_none(RouteAnnotation)
    component_url = component_route_annotation.url_path if component_route_annotation is not None else ''
    route_annotation = method.annotations.get_one_or_none(RouteAnnotation)
    url_path = component_url + ('' if route_annotation is None else route_annotation.url_path)
    return url_path
