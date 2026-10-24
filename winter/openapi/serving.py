import json
from functools import cache
from http import HTTPStatus
from typing import Any
from typing import Dict

import winter.web
from winter.application import Application
from .swagger_ui import get_swagger_ui_html


def serve_spec(app: Application, spec: Dict[str, Any], *, url: str):
    """
    Adds a route that serves the spec to the application. `url` is relative to the application root, like the url
    of any route. The servers of the spec are prefixed with the path the application is mounted at, so the spec stays
    right wherever the application is included.
    """

    @cache
    def body(mount_path: str) -> bytes:
        servers = spec.get('servers') or [{'url': '/'}]
        servers = [{**server, 'url': _join(mount_path, server['url'])} for server in servers]
        return json.dumps({**spec, 'servers': servers}).encode()

    class OpenAPISpec:
        @winter.web.route_get(url)
        def get(self, request: winter.web.Request) -> winter.web.Response:
            headers = {'content-type': 'application/json'}
            return winter.web.Response(HTTPStatus.OK, body(_mount_path(request, url)), headers)

    app.add(OpenAPISpec)


def serve_swagger_ui(app: Application, *, spec_url: str, url: str):
    """
    Adds a route with Swagger UI to the application, for the spec served at `spec_url`.
    Both urls are relative to the application root.
    """

    class SwaggerUI:
        @winter.web.route_get(url)
        def get(self, request: winter.web.Request) -> winter.web.Response:
            html = get_swagger_ui_html(openapi_url=_mount_path(request, url) + spec_url)
            return winter.web.Response(HTTPStatus.OK, html.encode(), {'content-type': 'text/html'})

    app.add(SwaggerUI)


def _mount_path(request: winter.web.Request, url: str) -> str:
    return request.path[:len(request.path) - len(url)]


def _join(mount_path: str, url: str) -> str:
    return mount_path.rstrip('/') + '/' + url.lstrip('/')
