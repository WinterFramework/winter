from typing import Optional
from typing import Tuple

from .route_annotation import RouteAnnotation
from ..core import Component
from ..core import ComponentMethod
from ..core import annotate
from ..http import MediaType
from ..routing.route import Route


def route(
        url_path: str,
        http_method: Optional[str] = None,
        produces: Optional[Tuple[MediaType]] = None,
        consumes: Optional[Tuple[MediaType]] = None,
):
    annotation = RouteAnnotation(url_path, http_method, produces, consumes)
    return annotate(annotation)


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


def get_route_annotation(component_method_or_component) -> Optional[RouteAnnotation]:
    if isinstance(component_method_or_component, ComponentMethod):
        annotations = component_method_or_component.annotations
        return annotations.get_one(RouteAnnotation)
    elif isinstance(component_method_or_component, Component):
        annotations = component_method_or_component.annotations
        return annotations.get_one_or_none(RouteAnnotation)
    else:
        raise AssertionError(f'invalid {component_method_or_component}')


def get_route(method: ComponentMethod) -> Route:
    component_route_annotation = get_route_annotation(method.component)
    component_url = component_route_annotation.url_path if component_route_annotation is not None else ''

    route_annotation = get_route_annotation(method)
    url_path = component_url + route_annotation.url_path
    route = Route(
        route_annotation.http_method,
        url_path,
        method,
        route_annotation.produces,
        route_annotation.consumes,
    )
    return route
