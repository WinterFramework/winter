from collections import defaultdict
from typing import List
from typing import Type
from typing import get_type_hints

import django.http
import rest_framework.authentication
import rest_framework.response
import rest_framework.views
import uritemplate
from django.conf.urls import url
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from .argument_resolver import resolve_arguments
from .controller import ControllerMethod
from .controller import get_controller_component
from .exceptions import WinterException
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


class WinterViewPrototype(rest_framework.views.APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)


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
    class WinterView(WinterViewPrototype):
        pass

    for controller_method in controller_methods:
        dispatch = _create_dispatch_function(controller, controller_method)
        dispatch.controller_method = controller_method
        dispatch_method_name = controller_method.http_method.lower()
        setattr(WinterView, dispatch_method_name, dispatch)
        generate_swagger_for_operation(dispatch, controller, controller_method)
    return WinterView().as_view()


def _create_dispatch_function(controller, controller_method: ControllerMethod):
    def dispatch(winter_view, request: Request, **path_variables):
        try:
            arguments = resolve_arguments(controller_method, request, path_variables)
            result = controller_method.func(controller, **arguments)
            if isinstance(result, django.http.HttpResponse):
                return result
            if isinstance(result, ResponseEntity):
                body = result.entity
                status_code = result.status_code
            else:
                body = result
                status_code = get_default_response_status(controller_method)
            output_processor = get_output_processor(controller_method.func, body)
            if output_processor:
                body = output_processor.process_output(body, request)
            if isinstance(body, django.http.HttpResponse):
                return body
            response = rest_framework.response.Response(body, status=status_code)
        except WinterException as exception:
            response = handle_winter_exception(exception)
        return response
    return dispatch


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
        regexp = '\d+' if issubclass(type_, int) else '\w+'
        url_path = url_path.replace(f'{{{variable_name}}}', f'(?P<{variable_name}>{regexp})')
    return url_path
