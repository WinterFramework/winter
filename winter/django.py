from collections import defaultdict
from typing import Any
from typing import List
from typing import Type

import django.http
import rest_framework.authentication
import rest_framework.response
import rest_framework.views
from django.conf.urls import url
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from .argument_resolver import arguments_resolver
from .controller import build_controller
from .controller import get_component
from .core import ComponentMethod
from .drf.auth import is_authentication_needed
from .exceptions import NotHandled
from .exceptions import WinterException
from .exceptions import exceptions_handler
from .exceptions import get_throws
from .exceptions import handle_winter_exception
from .http.throttling import create_throttle_classes
from .http.urls import rewrite_uritemplate_with_regexps
from .output_processor import get_output_processor
from .response_entity import ResponseEntity
from .response_status import get_default_response_status
from .routing.routing import Route
from .routing.routing import get_route
from .schema import generate_swagger_for_operation
from .schema.inspectors import SwaggerAutoSchema


class SessionAuthentication(rest_framework.authentication.SessionAuthentication):
    """SessionAuthentication with supporting 401 status code"""

    def authenticate_header(self, request):
        return 'Unauthorized'


def create_django_urls(controller_class: Type) -> List:
    component = get_component(controller_class)
    controller = build_controller(component.component_cls)
    django_urls = []

    for url_path, routes in _group_routes_by_url_path(component.methods):
        django_view = _create_django_view(controller, component, routes)
        winter_url_path = f'^{url_path}$'
        methods = (route.method for route in routes)
        django_url_path = rewrite_uritemplate_with_regexps(winter_url_path, methods)
        for route in routes:
            url_name = f'{controller_class.__name__}.{route.method.name}'
            django_urls.append(url(django_url_path, django_view, name=url_name))
    return django_urls


def _create_django_view(controller, component, routes: List[Route]):
    class WinterView(rest_framework.views.APIView):
        authentication_classes = (SessionAuthentication,)
        permission_classes = (IsAuthenticated,) if is_authentication_needed(component) else ()
        throttle_classes = create_throttle_classes(component, routes)
        swagger_schema = SwaggerAutoSchema

    for route in routes:
        dispatch = _create_dispatch_function(controller, route)
        dispatch.method = route.method
        dispatch_method_name = route.http_method.lower()
        setattr(WinterView, dispatch_method_name, dispatch)
        generate_swagger_for_operation(dispatch, controller, route)
    return WinterView().as_view()


def _create_dispatch_function(controller, route: Route):
    def dispatch(winter_view, request: Request, **path_variables):
        try:
            return _call_controller_method(controller, route, request)
        except WinterException as exception:
            return handle_winter_exception(exception)

    return dispatch


def _call_controller_method(controller, route: Route, request: Request):
    method = route.method
    arguments = arguments_resolver.resolve_arguments(route.method, request)
    try:
        result = method(controller, **arguments)
        return convert_result_to_http_response(request, result, route)
    except tuple(get_throws(method)) as e:
        result = exceptions_handler.handle(request, e)
        if result is NotHandled:
            raise
        return result


def convert_result_to_http_response(request: Request, result: Any, route: Route):
    if isinstance(result, django.http.HttpResponse):
        return result
    if isinstance(result, ResponseEntity):
        body = result.entity
        status_code = result.status_code
    else:
        body = result
        status_code = get_default_response_status(route)
    output_processor = get_output_processor(route.method, body)
    if output_processor is not None:
        body = output_processor.process_output(body, request)
    if isinstance(body, django.http.response.HttpResponseBase):
        return body
    return rest_framework.response.Response(body, status=status_code)


def _group_routes_by_url_path(methods: List[ComponentMethod]):
    result = defaultdict(list)
    for method in methods:
        route = get_route(method)
        result[route.url_path].append(route)
    return result.items()
