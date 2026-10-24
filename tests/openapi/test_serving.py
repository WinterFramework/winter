import json
from http import HTTPStatus

import pytest
from django.test import RequestFactory

import winter.django
import winter.openapi
import winter.web
from winter.application import Application
from winter.application import get_injector


@winter.web.problem(status=HTTPStatus.CONFLICT)
class _UndeclaredException(Exception):
    pass


class _API:
    @winter.web.route_get('v1/items/')
    def get_items(self) -> list[int]:  # pragma: no cover
        return []

    @winter.web.route_get('v1/orders/')
    def get_orders(self) -> list[int]:  # pragma: no cover
        return []


def _application(*definitions) -> Application:
    app = Application(modules=[], injector=get_injector())
    for definition in definitions:
        app.add(definition)
    return app


def _get(app: Application, route_name: str, path: str):
    [url] = [url for url in winter.django.create_urls(app) if url.name == route_name]
    return url.callback(RequestFactory().get(path))


def test_generate_openapi_of_application():
    app = _application(_API)

    # Act
    spec = winter.openapi.generate_openapi(app, title='title', version='1.0.0')

    # Assert
    assert list(spec['paths']) == ['/items/', '/orders/']
    assert spec['servers'] == [{'url': '/v1'}]


def test_generate_openapi_requires_raises_annotations():
    app = _application(_API, _UndeclaredException)

    # Act
    with pytest.raises(AssertionError, match='_UndeclaredException'):
        winter.openapi.generate_openapi(app, title='title', version='1.0.0')


def test_generate_openapi_allows_missing_raises_annotations():
    app = _application(_API, _UndeclaredException)

    # Act
    spec = winter.openapi.generate_openapi(app, title='title', version='1.0.0', allow_missing_raises_annotation=True)

    # Assert
    assert list(spec['paths']) == ['/items/', '/orders/']


def test_serve_spec_prefixes_servers_with_mount_path():
    app = _application(_API)
    spec = winter.openapi.generate_openapi(app, title='title', version='1.0.0')
    winter.openapi.serve_spec(app, spec, url='openapi.json')

    # Act
    response = _get(app, 'OpenAPISpec.get', '/service/openapi.json')

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response['content-type'] == 'application/json'
    served_spec = json.loads(response.content)
    assert served_spec['servers'] == [{'url': '/service/v1'}]
    assert served_spec['paths'] == spec['paths']
    assert spec['servers'] == [{'url': '/v1'}]


def test_serve_spec_without_servers():
    app = _application()
    winter.openapi.serve_spec(app, {'openapi': '3.0.3'}, url='docs/openapi.json')

    # Act
    response = _get(app, 'OpenAPISpec.get', '/service/docs/openapi.json')

    # Assert
    assert json.loads(response.content) == {'openapi': '3.0.3', 'servers': [{'url': '/service/'}]}


def test_serve_swagger_ui_points_to_spec_under_mount_path():
    app = _application()
    winter.openapi.serve_swagger_ui(app, spec_url='openapi.json', url='docs/')

    # Act
    response = _get(app, 'SwaggerUI.get', '/service/docs/')

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response['content-type'] == 'text/html'
    assert "url: '/service/openapi.json'" in response.content.decode()
