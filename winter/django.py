from collections import defaultdict
from typing import List
from typing import Type

import django.http
import rest_framework.authentication
import rest_framework.response
import rest_framework.views
from django.conf.urls import url
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from winter.routing import rewrite_uritemplate_with_regexps
from .argument_resolver import arguments_resolver
from .controller import ControllerMethod
from .controller import get_controller_component
from .drf.auth import is_authentication_needed
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


def create_django_urls(controller_class: Type) -> List:
    controller_component = get_controller_component(controller_class)
    assert controller_component, f'{controller_class} is not marked as controller'
    injector = get_injector()
    if injector:
        controller = injector.get(controller_class)
    else:
        controller = controller_class()
    django_urls = []
    funcs = [a.func for a in controller_component.methods]
    root_route = get_function_route(controller_class) or Route('')
    root_url = rewrite_uritemplate_with_regexps(root_route.url_path, funcs)

    for url_path, controller_methods in _group_methods_by_url_path(controller_component.methods):
        django_view = _create_django_view(controller, controller_methods)
        django_url_path = f'^{root_url}{url_path}$'
        for controller_method in controller_methods:
            url_name = f'{controller_class.__name__}.{controller_method.name}'
            django_urls.append(url(django_url_path, django_view, name=url_name))
    return django_urls


def _create_django_view(controller, controller_methods: List[ControllerMethod]):
    class WinterView(rest_framework.views.APIView):
        authentication_classes = (SessionAuthentication,)
        permission_classes = (IsAuthenticated,) if is_authentication_needed(controller.__class__) else ()

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
            arguments = arguments_resolver.resolve_arguments(controller_method, request, path_variables)
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
            if output_processor is not None:
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
        result[controller_method.url].append(controller_method)
    return result.items()
