from collections import defaultdict
from functools import wraps
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
from .exceptions.handlers import MethodExceptionsHandler
from .http import ResponseEntity
from .http.default_response_status import get_default_response_status
from .http.throttling import create_throttle_classes
from .http.urls import rewrite_uritemplate_with_regexps
from .output_processor import get_output_processor
from .routing.routing import Route
from .routing.routing import get_route


class SessionAuthentication(rest_framework.authentication.SessionAuthentication):
    """SessionAuthentication with supporting 401 status code"""

    def authenticate_header(self, request):
        return 'Unauthorized'


def create_django_urls(controller_class: Type) -> List:
    component = get_component(controller_class)
    django_urls = []

    for url_path, routes in _group_routes_by_url_path(component.methods):
        django_view = _create_django_view(controller_class, component, routes)
        winter_url_path = f'^{url_path}$'
        methods = (route.method for route in routes)
        django_url_path = rewrite_uritemplate_with_regexps(winter_url_path, methods)
        for route in routes:
            django_urls.append(url(django_url_path, django_view, name=route.method.full_name))
    return django_urls


def _create_django_view(controller_class, component, routes: List[Route]):
    class WinterView(rest_framework.views.APIView):
        authentication_classes = (SessionAuthentication,)
        permission_classes = (IsAuthenticated,) if is_authentication_needed(component) else ()
        throttle_classes = create_throttle_classes(routes)

    # It's useful for New Relic APM
    WinterView.__module__ = controller_class.__module__
    WinterView.__qualname__ = controller_class.__qualname__

    for route in routes:
        dispatch = _create_dispatch_function(controller_class, route)
        dispatch.route = route
        dispatch_method_name = route.http_method.lower()
        setattr(WinterView, dispatch_method_name, dispatch)
    return WinterView().as_view()


def _create_dispatch_function(controller_class, route: Route):
    component = get_component(controller_class)

    @wraps(route.method.func)
    def dispatch(winter_view, request: Request, **path_variables):
        controller = build_controller(component.component_cls)
        return _call_controller_method(controller, route, request)

    return dispatch


def _call_controller_method(controller, route: Route, request: Request):
    method = route.method
    method_exceptions_handler = MethodExceptionsHandler(method)
    response_headers = {}
    try:
        arguments = arguments_resolver.resolve_arguments(method, request, response_headers)
        result = method(controller, **arguments)
        response = convert_result_to_http_response(request, result, method)
    except method_exceptions_handler.exception_classes as exception:
        response = method_exceptions_handler.handle(exception, request, response_headers)
        if response is None:
            raise

    _fill_response_headers(response, response_headers)
    return response


def _fill_response_headers(response, response_headers):
    from .http import response_headers_serializer

    for header_name, header_value in response_headers.items():
        response[header_name] = response_headers_serializer.serialize(header_value, header_name)


def convert_result_to_http_response(request: Request, result: Any, method: ComponentMethod):
    if isinstance(result, django.http.HttpResponse):
        return result
    if isinstance(result, ResponseEntity):
        body = result.entity
        status_code = result.status_code
    else:
        body = result
        status_code = get_default_response_status(request.method, method)
    output_processor = get_output_processor(method, body)
    if output_processor is not None:
        body = output_processor.process_output(body, request)
    if isinstance(body, django.http.response.HttpResponseBase):
        return body
    return rest_framework.response.Response(body, status=status_code)


def _group_routes_by_url_path(methods: List[ComponentMethod]):
    result = defaultdict(list)
    for method in methods:
        route = get_route(method)
        if route is not None:
            result[route.url_path].append(route)
    return result.items()
