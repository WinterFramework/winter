from collections import defaultdict
from functools import wraps
from typing import List
from typing import TYPE_CHECKING

import django.http
from django.http.response import HttpResponseBase
from django.urls import URLPattern
from django.urls import re_path

import winter.web.initialization
from winter.application import Application
from winter.web import Response
from winter.web import arguments_resolver
from winter.web import handle_request
from winter.web import register_native_response_type
from winter.web import set_throttling_identity_resolver
from winter.web.autodiscovery import find_routes
from winter.web.routing import Route
from winter.web.urls import rewrite_uritemplate_with_regexps
from .http_request_argument_resolver import HttpRequestArgumentResolver
from .request import DjangoRequest
from .throttling import django_user_identity

if TYPE_CHECKING:
    from django.views.generic import View


def create_urls(app: Application) -> List[URLPattern]:
    """URL patterns of the routes of an application, relative to where they are included in the urlpatterns."""
    winter.web.initialization.initialize(app)
    _initialize_process()
    return _create_urls_from_routes(find_routes(app))


_process_initialized = False


def _initialize_process():
    """Process-global until the registries move into Application: docs/architecture.md, Current deviations."""
    global _process_initialized
    if not _process_initialized:
        arguments_resolver.add_argument_resolver(HttpRequestArgumentResolver())
        register_native_response_type(HttpResponseBase)
        set_throttling_identity_resolver(django_user_identity)
        _process_initialized = True


def _create_urls_from_routes(routes: List[Route]) -> List[URLPattern]:
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
        dispatch = _create_dispatch_function(route)
        dispatch.route = route
        dispatch_method_name = route.http_method.lower()
        setattr(WinterView, dispatch_method_name, dispatch)

    return WinterView()


def _create_dispatch_function(route: Route):
    @wraps(route.method.func)
    def dispatch(winter_view, request: django.http.HttpRequest, **path_parameters):
        response = handle_request(route, DjangoRequest(request, path_parameters))
        return to_django_response(response)

    return dispatch


def to_django_response(response: Response) -> HttpResponseBase:
    if isinstance(response.body, HttpResponseBase):
        django_response = response.body
    else:
        django_response = django.http.HttpResponse(response.body, status=response.status_code)
    for header_name, header_value in response.headers.items():
        django_response[header_name] = header_value
    return django_response
