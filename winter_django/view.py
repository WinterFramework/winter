from collections import defaultdict
from functools import wraps
from typing import Any
from typing import List
from typing import Type
from typing import TYPE_CHECKING

import django.http
import rest_framework.authentication
import rest_framework.response
from django.conf.urls import url
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from winter.core import Component
from winter.core import ComponentMethod
from winter.core import get_injector
from winter.web import ResponseEntity
from winter.web import response_headers_serializer
from winter.web.argument_resolver import arguments_resolver
from winter.web.auth import is_authentication_needed
from winter.web.default_response_status import get_default_response_status
from winter.web.exceptions import MethodExceptionsManager
from winter.web.exceptions import ThrottleException
from winter.web.interceptor import interceptor_registry
from winter.web.output_processor import get_output_processor
from winter.web.routing import Route
from winter.web.routing import get_route
from winter.web.throttling import create_throttle_class
from winter.web.urls import rewrite_uritemplate_with_regexps


if TYPE_CHECKING:
    import rest_framework.views


class SessionAuthentication(rest_framework.authentication.SessionAuthentication):
    """SessionAuthentication with supporting 401 status code"""

    def authenticate_header(self, request):
        return 'Unauthorized'


def create_django_urls(api_class_with_routes: Type) -> List:
    component = Component.get_by_cls(api_class_with_routes)
    django_urls = []

    for url_path, routes in _group_routes_by_url_path(component.methods):
        django_view = create_drf_view(api_class_with_routes, routes).as_view()
        winter_url_path = f'^{url_path}$'
        methods = [route.method for route in routes]
        django_url_path = rewrite_uritemplate_with_regexps(winter_url_path, methods)
        for route in routes:
            django_urls.append(url(django_url_path, django_view, name=route.method.full_name))
    return django_urls


def create_drf_view(api_class: Type, routes: List[Route]) -> 'rest_framework.views.APIView':
    import rest_framework.views

    component = Component.get_by_cls(api_class)

    class WinterView(rest_framework.views.APIView):
        authentication_classes = (SessionAuthentication,)
        permission_classes = (IsAuthenticated,) if is_authentication_needed(component) else ()

    # It's useful for New Relic APM
    WinterView.__module__ = api_class.__module__
    WinterView.__qualname__ = api_class.__qualname__

    for route in routes:
        dispatch = _create_dispatch_function(api_class, route)
        dispatch.route = route
        dispatch_method_name = route.http_method.lower()
        setattr(WinterView, dispatch_method_name, dispatch)
    return WinterView()


def _create_dispatch_function(api_class: Type, route: Route):
    component = Component.get_by_cls(api_class)

    @wraps(route.method.func)
    def dispatch(winter_view, request: Request, **path_variables):
        api_class_instance = get_injector().get(component.component_cls)
        return _call_api(api_class_instance, route, request)

    return dispatch


def _call_api(api_class_instance, route: Route, request: Request):
    method = route.method
    method_exceptions_manager = MethodExceptionsManager(method)
    response_headers = {}

    throttle_class = create_throttle_class(route)
    try:
        if throttle_class and not throttle_class.allow_request(request):
            raise ThrottleException()

        for interceptor in interceptor_registry:
            pre_handle = ComponentMethod.get_or_create(interceptor.__class__.pre_handle)
            arguments = arguments_resolver.resolve_arguments(
                pre_handle, request, response_headers, {
                    'method': method,
                },
            )
            pre_handle(interceptor, **arguments)

        arguments = arguments_resolver.resolve_arguments(method, request, response_headers)
        result = method(api_class_instance, **arguments)
    except method_exceptions_manager.exception_classes as exception:
        handler = method_exceptions_manager.get_handler(exception)
        if handler is None:
            raise

        method = ComponentMethod.get_or_create(handler.__class__.handle)
        arguments = arguments_resolver.resolve_arguments(
            method, request, response_headers, {
                'exception': exception,
                'response_headers': response_headers,
            },
        )
        result = method(handler, **arguments)

    response = convert_result_to_http_response(request, result, method)
    _fill_response_headers(response, response_headers)
    return response


def _fill_response_headers(response, response_headers):
    for header_name, header_value in response_headers.items():
        response[header_name] = response_headers_serializer.serialize(header_value, header_name)
    response.content_type = response_headers.get('content-type')


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
