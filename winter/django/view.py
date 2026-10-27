from collections import defaultdict
from functools import wraps
from typing import List
from typing import TYPE_CHECKING

import django.http
from django.http.response import HttpResponseBase
from django.urls import URLPattern
from django.urls import re_path

from winter.web import Response
from winter.web import WebApplication
from winter.web import handle_request
from winter.web import register_native_response_type
from winter.web.autodiscovery import find_routes
from winter.web.exception_handlers import find_exception_handlers
from winter.web.exceptions import ExceptionHandlers
from winter.web.request_handler import check_arguments
from winter.web.routing import Route
from winter.web.urls import rewrite_uritemplate_with_regexps
from .request import DjangoRequest
from .throttling import django_user_identity

if TYPE_CHECKING:
    from django.views.generic import View


def create_urls(app: WebApplication) -> List[URLPattern]:
    """URL patterns of the routes of an application, relative to where they are included in the urlpatterns."""
    _initialize_process()
    routes = find_routes(app)
    exception_handlers = find_exception_handlers(app)
    # Each request binds the Django request, see _create_dispatch_function
    check_arguments(app, routes, exception_handlers, request_types=[django.http.HttpRequest])
    return _create_urls_from_routes(app, routes, exception_handlers)


_process_initialized = False


def _initialize_process():
    """Process-global until native response types belong to an application: docs/architecture.md, Current deviations."""
    global _process_initialized
    if not _process_initialized:
        register_native_response_type(HttpResponseBase)
        _process_initialized = True


def _create_urls_from_routes(
    app: WebApplication,
    routes: List[Route],
    exception_handlers: ExceptionHandlers,
) -> List[URLPattern]:
    django_urls = []
    grouped_routes = defaultdict(list)

    for route in routes:
        grouped_routes[route.url_path].append(route)

    for url_path, routes in grouped_routes.items():
        django_view = _create_django_view_from_routes(app, routes, exception_handlers).as_view()
        winter_url_path = f'^{url_path}$'
        methods = [route.method for route in routes]
        django_url_path = rewrite_uritemplate_with_regexps(winter_url_path, methods)

        for route in routes:
            django_url = re_path(django_url_path, django_view, name=route.method.full_name)
            django_urls.append(django_url)

    return django_urls


def _create_django_view_from_routes(
    app: WebApplication,
    routes: List[Route],
    exception_handlers: ExceptionHandlers,
) -> 'View':
    from django.views.generic import View

    class WinterView(View):
        @classmethod
        def as_view(cls, **initkwargs):
            return super().as_view(**initkwargs)

    for route in routes:
        dispatch = _create_dispatch_function(app, route, exception_handlers)
        dispatch.route = route
        dispatch_method_name = route.http_method.lower()
        setattr(WinterView, dispatch_method_name, dispatch)

    return WinterView()


def _create_dispatch_function(app: WebApplication, route: Route, exception_handlers: ExceptionHandlers):
    @wraps(route.method.func)
    def dispatch(winter_view, request: django.http.HttpRequest, **path_parameters):
        winter_request = DjangoRequest(request, path_parameters)
        request_values = {django.http.HttpRequest: request}
        response = handle_request(app, route, winter_request, exception_handlers, request_values, django_user_identity)
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
