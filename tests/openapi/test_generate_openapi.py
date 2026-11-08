from http import HTTPStatus

import pytest

import winter.openapi
import winter.web
from tests.injection import app_injector


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


def _application(*definitions) -> winter.web.WebApplication:
    app = winter.web.WebApplication(modules=[], injector=app_injector)
    for definition in definitions:
        app.add(definition)
    return app


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
