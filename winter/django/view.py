import inspect
from collections import defaultdict
from functools import wraps
from typing import Dict
from typing import List
from typing import Optional

import django.http
from django.http.response import HttpResponseBase
from django.urls import Resolver404
from django.urls import ResolverMatch
from django.urls import URLPattern
from django.urls import re_path
from django.urls import resolve
from django.views import View

from winter.web import Response
from winter.web import WebApplication
from winter.web import handle_request
from winter.web.autodiscovery import find_routes
from winter.web.exception_handlers import check_raises
from winter.web.exception_handlers import find_exception_handlers
from winter.web.exceptions import ExceptionHandlers
from winter.web.request_handler import check_arguments
from winter.web.routing import Route
from winter.web.urls import rewrite_uritemplate_with_regexps
from .request import DjangoRequest
from .throttling import django_user_identity


class _WinterView(View):
    """The view of the routes of one URL path, by their HTTP methods."""
    routes: Dict[str, Route]


def create_urls(app: WebApplication, prefix: str = '') -> List[URLPattern]:
    """
    URL patterns of the routes of an application under the path prefix, such as `public-api/v1/`. The routes of the
    requests carry the prefix, unlike the prefix of a Django include, which Winter does not see.
    """
    routes = [route.with_prefix(prefix) for route in find_routes(app)]
    exception_handlers = find_exception_handlers(app)
    # Each request binds the Django request, see _create_dispatch_function
    check_arguments(app, routes, exception_handlers, request_types=[django.http.HttpRequest])
    check_raises(routes, exception_handlers)
    return _create_urls_from_routes(app, routes, exception_handlers)


def route_of(request: django.http.HttpRequest) -> Optional[Route]:
    """
    The route that Winter serves the request with, None for a request that Winter does not serve. The URL is resolved
    here when Django has not resolved it yet, so that a middleware may ask before calling the view. A HEAD request is
    served with the GET route, as Django does.
    """
    match = request.resolver_match or _resolve(request)
    view_class = getattr(match.func, 'view_class', None) if match is not None else None
    if not (inspect.isclass(view_class) and issubclass(view_class, _WinterView)):
        return None
    return view_class.routes.get('GET' if request.method == 'HEAD' else request.method)


def _resolve(request: django.http.HttpRequest) -> Optional[ResolverMatch]:
    try:
        return resolve(request.path_info, urlconf=getattr(request, 'urlconf', None))
    except Resolver404:
        return None


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
) -> type[_WinterView]:
    view_class = type('WinterView', (_WinterView,), {'routes': {route.http_method: route for route in routes}})
    for route in routes:
        setattr(view_class, route.http_method.lower(), _create_dispatch_function(app, route, exception_handlers))
    return view_class


def _create_dispatch_function(app: WebApplication, route: Route, exception_handlers: ExceptionHandlers):
    @wraps(route.method.func)
    def dispatch(winter_view, request: django.http.HttpRequest, **path_parameters):
        winter_request = DjangoRequest(request, path_parameters)
        request_values = {django.http.HttpRequest: request}
        response = handle_request(
            app,
            route,
            winter_request,
            exception_handlers,
            request_values,
            throttling_identity=django_user_identity,
            native_response_types=(HttpResponseBase,),
        )
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
