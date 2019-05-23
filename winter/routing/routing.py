from typing import List
from typing import Optional
from typing import Tuple

from uritemplate import URITemplate

from .route_annotation import RouteAnnotation
from ..core import ComponentMethod
from ..core import annotate
from ..http import MediaType
from ..query_parameters import QueryParameterAnnotation
from ..routing.route import Route


def route(
        url_path: str,
        http_method: Optional[str] = None,
        produces: Optional[Tuple[MediaType]] = None,
        consumes: Optional[Tuple[MediaType]] = None,
):
    route_annotation = RouteAnnotation(url_path, http_method, produces, consumes)
    query_annotations = get_query_param_annotations(url_path)

    def wrapper(func_or_method):
        annotate_ = annotate(route_annotation, single=True)
        method = annotate_(func_or_method)
        if hasattr(method, 'annotations'):
            existing_annotations = method.annotations.get(QueryParameterAnnotation)
        else:
            existing_annotations = []

        for query_annotation in query_annotations:
            for existing_annotation in existing_annotations:
                if existing_annotation.map_to == query_annotation.map_to:
                    raise ValueError(f'The argument is already mapped '
                                     f'from {existing_annotation.name}: {query_annotation.name}')

        for query_annotation in query_annotations:
            for existing_annotation in existing_annotations:
                if existing_annotation.name == query_annotation.name:
                    existing_annotation.explode = query_annotation.explode
                    break
            else:
                annotate_ = annotate(query_annotation, unique=True)
                method = annotate_(method)

        return method

    return wrapper


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


def get_route(method: ComponentMethod) -> Route:
    route_annotation = method.annotations.get_one(RouteAnnotation)
    url_path = get_url_path(method)
    route = Route(
        route_annotation.http_method,
        url_path,
        method,
        route_annotation.produces,
        route_annotation.consumes,
    )
    return route


def get_url_path(method: ComponentMethod) -> str:
    route_annotations = method.component.annotations
    component_route_annotation = route_annotations.get_one_or_none(RouteAnnotation)
    component_url = component_route_annotation.url_path if component_route_annotation is not None else ''
    route_annotation = method.annotations.get_one(RouteAnnotation)
    url_path = component_url + route_annotation.url_path
    return url_path


def get_query_param_annotations(url_path: str) -> List[QueryParameterAnnotation]:
    query_param_annotations = []
    query_variables = (variable for variable in URITemplate(url_path).variables if variable.operator == '?')
    for variable in query_variables:
        for variable_name, variable_params in variable.variables:
            annotation = QueryParameterAnnotation(name=variable_name, explode=variable_params['explode'])
            query_param_annotations.append(annotation)
    return query_param_annotations
