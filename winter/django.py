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
from .exceptions.handlers import MethodExceptionsHandler
from .exceptions.handlers import NotHandled
from .exceptions.handlers import exceptions_handler
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
    django_urls = []

    for url_path, routes in _group_routes_by_url_path(component.methods):
        django_view = _create_django_view(controller_class, component, routes)
        winter_url_path = f'^{url_path}$'
        methods = (route.method for route in routes)
        django_url_path = rewrite_uritemplate_with_regexps(winter_url_path, methods)
        for route in routes:
            url_name = f'{controller_class.__name__}.{route.method.name}'
            django_urls.append(url(django_url_path, django_view, name=url_name))
    return django_urls


def _create_django_view(controller_class, component, routes: List[Route]):
    class WinterView(rest_framework.views.APIView):
        authentication_classes = (SessionAuthentication,)
        permission_classes = (IsAuthenticated,) if is_authentication_needed(component) else ()
        throttle_classes = create_throttle_classes(component, routes)
        swagger_schema = SwaggerAutoSchema

    for route in routes:
        dispatch = _create_dispatch_function(controller_class, route)
        dispatch.method = route.method
        dispatch_method_name = route.http_method.lower()
        setattr(WinterView, dispatch_method_name, dispatch)
        generate_swagger_for_operation(dispatch, controller_class, route)
    return WinterView().as_view()


def _create_dispatch_function(controller_class, route: Route):
    component = get_component(controller_class)

    def dispatch(winter_view, request: Request, **path_variables):
        controller = build_controller(component.component_cls)
        return _call_controller_method(controller, route, request)

    return dispatch


def _call_controller_method(controller, route: Route, request: Request):
    method = route.method
    method_exceptions_handler = MethodExceptionsHandler(method)
    try:
        arguments = arguments_resolver.resolve_arguments(method, request)
        result = method(controller, **arguments)
        return convert_result_to_http_response(request, result, method)
    except method_exceptions_handler.exception_classes as exception:
        result = method_exceptions_handler.handle(request, exception)
        if result is NotHandled:
            raise
        return result
    except exceptions_handler.auto_handle_exception_classes as exception:
        return exceptions_handler.handle(request, exception)


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
        result[route.url_path].append(route)
    return result.items()
