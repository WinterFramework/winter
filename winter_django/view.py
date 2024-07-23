import json
from collections import defaultdict
from functools import wraps
from typing import Any
from typing import List
from typing import TYPE_CHECKING
from typing import Type

import django.http
from django.urls import re_path
from django.urls import URLPattern

from winter.core import Component
from winter.core import ComponentMethod
from winter.core import get_injector
from winter.core.json import JSONEncoder
from winter.web import ResponseEntity
from winter.web import exception_handlers_registry
from winter.web import response_headers_serializer
from winter.web.argument_resolver import arguments_resolver
from winter.web.default_response_status import get_response_status
from winter.web.exceptions import MethodExceptionsManager
from winter.web.exceptions import ThrottleException
from winter.web.interceptor import interceptor_registry
from winter.web.output_processor import get_output_processor
from winter.web.routing import Route
from winter.web.throttling import create_throttle_class
from winter.web.urls import rewrite_uritemplate_with_regexps

if TYPE_CHECKING:
    from django.views.generic import View


def create_django_urls_from_routes(routes: List[Route]) -> List[URLPattern]:
    django_urls = []
    grouped_routes = defaultdict(list)

    for route in routes:
        grouped_routes[route.url_path].append(route)

    for url_path, routes in grouped_routes.items():
        django_view = _create_django_view_from_routes(routes).as_view()
        winter_url_path = f'^{url_path}$'
        methods = [route.method for route in routes]
        django_url_path = rewrite_uritemplate_with_regexps(winter_url_path, methods)

        for route in routes:
            django_url = re_path(django_url_path, django_view, name=route.method.full_name)
            django_urls.append(django_url)

    return django_urls


def _create_django_view_from_routes(routes: List[Route]) -> 'View':
    from django.views.generic import View

    class WinterView(View):
        @classmethod
        def as_view(cls, **initkwargs):
            return super().as_view(**initkwargs)

    for route in routes:
        dispatch = _create_dispatch_function(route.method.component.component_cls, route)
        dispatch.route = route
        dispatch_method_name = route.http_method.lower()
        setattr(WinterView, dispatch_method_name, dispatch)

    return WinterView()


def _create_dispatch_function(api_class: Type, route: Route):
    component = Component.get_by_cls(api_class)

    @wraps(route.method.func)
    def dispatch(winter_view, request: django.http.HttpRequest, **path_variables):
        api_class_instance = get_injector().get(component.component_cls)
        return _call_api(api_class_instance, route, request)

    return dispatch


def _call_api(api_class_instance, route: Route, request: django.http.HttpRequest):
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
    except Exception as exception:
        handler = method_exceptions_manager.get_handler(exception)
        method = ComponentMethod.get_or_create(handler.__class__.handle)
        try:
            arguments = arguments_resolver.resolve_arguments(
                method, request, response_headers, {
                    'exception': exception,
                    'response_headers': response_headers,
                },
            )
            result = method(handler, **arguments)
        except Exception as inner_exception:
            handler = exception_handlers_registry.get_default_handler()
            method = ComponentMethod.get_or_create(handler.__class__.handle)
            arguments = arguments_resolver.resolve_arguments(
                method, request, response_headers, {
                    'exception': inner_exception,
                    'response_headers': response_headers,
                },
            )
            result = method(handler, **arguments)

    response = _convert_result_to_http_response(request, result, method)
    _fill_response_headers(response, response_headers)
    return response


def _fill_response_headers(response, response_headers):
    for header_name, header_value in response_headers.items():
        response[header_name] = response_headers_serializer.serialize(header_value, header_name)
    response.content_type = response_headers.get('content-type')


def _convert_result_to_http_response(request: django.http.HttpRequest, result: Any, method: ComponentMethod):
    if isinstance(result, django.http.HttpResponse):
        return result
    if isinstance(result, ResponseEntity):
        body = result.entity
        status_code = result.status_code
    else:
        body = result
        status_code = get_response_status(request.method, method)
    output_processor = get_output_processor(method, body)
    if output_processor is not None:
        body = output_processor.process_output(body, request)
    if isinstance(body, django.http.response.HttpResponseBase):
        return body
    if body is None:
        content = b''
    else:
        content = json.dumps(body, cls=JSONEncoder).encode()
    return django.http.HttpResponse(content, status=status_code, content_type='application/json')
