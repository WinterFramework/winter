from collections import defaultdict
from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import get_type_hints
from uuid import UUID

import django.http
import rest_framework.authentication
import rest_framework.response
import rest_framework.views
import uritemplate
from django.conf.urls import url
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BaseRenderer
from rest_framework.request import Request

from .argument_resolver import arguments_resolver
from .controller import ControllerMethod
from .controller import get_controller_component
from .drf.auth import is_authentication_needed
from .exceptions import NotHandled
from .exceptions import WinterException
from .exceptions import exceptions_handler
from .exceptions import get_throws
from .exceptions import handle_winter_exception
from .injection import get_injector
from .output_processor import get_output_processor
from .response_entity import ResponseEntity
from .response_status import get_default_response_status
from .routing import Route
from .routing import get_function_route
from .schema import generate_swagger_for_operation


class SessionAuthentication(rest_framework.authentication.SessionAuthentication):
    """SessionAuthentication with supporting 401 status code"""
    def authenticate_header(self, request):
        return 'Unauthorized'


def create_django_urls(controller_class: Type) -> List:
    controller_component = get_controller_component(controller_class)
    assert controller_component, f'{controller_class} is not marked as controller'
    injector = get_injector()
    if injector:
        controller = injector.get(controller_class)
    else:
        controller = controller_class()
    django_urls = []
    root_route = get_function_route(controller_class) or Route('')
    for url_path, controller_methods in _group_methods_by_url_path(controller_component.methods):
        django_view = _create_django_view(controller, controller_methods)
        winter_url_path = f'^{root_route.url_path}{url_path}$'
        django_url_path = _rewrite_uritemplate_with_regexps(winter_url_path, controller_methods)
        for controller_method in controller_methods:
            url_name = f'{controller_class.__name__}.{controller_method.name}'
            django_urls.append(url(django_url_path, django_view, name=url_name))
    return django_urls


def _create_django_view(controller, controller_methods: List[ControllerMethod]):
    class WinterView(rest_framework.views.APIView):
        authentication_classes = (SessionAuthentication,)
        permission_classes = (IsAuthenticated,) if is_authentication_needed(controller.__class__) else ()
        renderer_classes = _get_renderer_classes(controller_methods)

    for controller_method in controller_methods:
        dispatch = _create_dispatch_function(controller, controller_method)
        dispatch.controller_method = controller_method
        dispatch_method_name = controller_method.http_method.lower()
        setattr(WinterView, dispatch_method_name, dispatch)
        generate_swagger_for_operation(dispatch, controller, controller_method)
    return WinterView().as_view()


def _get_renderer_classes(controller_methods) -> List[BaseRenderer]:
    renderer_classes = []
    for controller_method in controller_methods:
        route = get_function_route(controller_method.func)
        if not route.produces:
            continue

        for media_type_ in route.produces:
            class Renderer(BaseRenderer):
                """The renderer bypasses rendering, but adds media_type info, which is used by swagger."""
                media_type = str(media_type_)

                def render(self, data, accepted_media_type=None, renderer_context=None):
                    return data

            renderer_classes.append(Renderer)
    renderer_classes = tuple(renderer_classes) or rest_framework.views.APIView.renderer_classes
    return renderer_classes


def _create_dispatch_function(controller, controller_method: ControllerMethod):
    def dispatch(winter_view, request: Request, **path_variables):
        try:
            return _call_controller_method(controller, controller_method, path_variables, request)
        except WinterException as exception:
            return handle_winter_exception(exception)

    return dispatch


def _call_controller_method(controller, controller_method: ControllerMethod, path_variables: Dict, request: Request):
    arguments = arguments_resolver.resolve_arguments(controller_method, request, path_variables)
    try:
        result = controller_method.func(controller, **arguments)
        return convert_result_to_http_response(request, result, controller_method.func)
    except tuple(get_throws(controller_method.func)) as e:
        result = exceptions_handler.handle(request, e)
        if result is NotHandled:
            raise
        return result


def convert_result_to_http_response(request: Request, result: Any, handle_func):
    if isinstance(result, django.http.HttpResponse):
        return result
    if isinstance(result, ResponseEntity):
        body = result.entity
        status_code = result.status_code
    else:
        body = result
        status_code = get_default_response_status(handle_func, request.method)
    output_processor = get_output_processor(handle_func, body)
    if output_processor is not None:
        body = output_processor.process_output(body, request)
    if isinstance(body, django.http.response.HttpResponseBase):
        return body
    return rest_framework.response.Response(body, status=status_code)


def _group_methods_by_url_path(controller_methods: List[ControllerMethod]):
    result = defaultdict(list)
    for controller_method in controller_methods:
        result[controller_method.url_path].append(controller_method)
    return result.items()


def _rewrite_uritemplate_with_regexps(winter_url_path: str, methods: List[ControllerMethod]) -> str:
    url_path = winter_url_path
    for variable_name in uritemplate.variables(winter_url_path):
        types = {get_type_hints(method.func).get(variable_name) for method in methods} or {None}
        if len(types) > 1:
            raise Exception(f'Different methods are bound to the same path variable, but have different types annotated: {types}')
        type_, = types
        regexp = _get_regexp(type_)
        url_path = url_path.replace(f'{{{variable_name}}}', f'(?P<{variable_name}>{regexp})')
    return url_path


def _get_regexp(type_) -> str:
    if issubclass(type_, int):
        return r'\d+'
    elif issubclass(type_, UUID):
        return r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    else:
        return r'[^/]+'
