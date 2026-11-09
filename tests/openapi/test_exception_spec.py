from dataclasses import dataclass
from http import HTTPStatus

import pytest

import winter.openapi
import winter.web
from tests.injection import app_injector
from tests.web_application import web_application
from winter.web.routing import get_route
from winter.openapi.generator import generate_openapi_for_routes
from winter.openapi.annotations import global_exception


def test_global_exception_annotated_on_method():
    @global_exception
    class GlobalException(Exception):
        pass

    class _Handlers:
        @winter.web.exception_handler
        @winter.web.response_status(HTTPStatus.CONFLICT)
        def handle(self, exception: GlobalException):  # pragma: no cover
            pass

    class _TestAPI:
        @winter.web.raises(GlobalException)
        @winter.web.route_get('resource')
        def get_resource(self):  # pragma: no cover
            pass

    app = web_application(GlobalException, _Handlers, _TestAPI, injector=app_injector)

    # Act
    result = winter.openapi.generate_openapi(app, title='title', version='1.0.0')

    # Assert
    assert result['paths']['/resource']['get']['responses'] == {'200': {'description': ''}, '409': {'description': ''}}


def test_exception_declared_with_raises_without_handler_fails():
    class _Error(Exception):
        pass

    class _TestAPI:
        @winter.web.raises(_Error)
        @winter.web.route_get('resource')
        def get_resource(self):  # pragma: no cover
            pass

    # Act
    with pytest.raises(ValueError) as exception_info:
        generate_openapi_for_routes(title='title', version='1.0.0', routes=[get_route(_TestAPI.get_resource)])

    # Assert
    assert str(exception_info.value) == (
        '_Error is declared with @raises in _TestAPI.get_resource and has no handler in the application'
    )


@dataclass
class ProblemExistsExceptionDTO:
    message: str


@pytest.mark.parametrize(
    'handler_return_type, handler_spec, expected_components', [
        (
            ProblemExistsExceptionDTO,
            {
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': '#/components/schemas/ProblemExistsExceptionDTO'
                        },
                    },
                },
            },
            {
                'schemas': {
                    'ProblemExistsExceptionDTO': {
                        'description': 'ProblemExistsExceptionDTO(message: str)',
                        'properties': {'message': {'type': 'string'}},
                        'required': ['message'],
                        'title': 'ProblemExistsExceptionDTO',
                        'type': 'object',
                    },
                },
                'parameters': {},
                'responses': {},
            }
        ),
        (None, {'description': ''}, {'parameters': {}, 'responses': {}, 'schemas': {}}),
    ],
)
def test_response_of_raised_exception_is_that_of_its_handler_in_application(
    handler_return_type,
    handler_spec,
    expected_components,
):
    class ProblemExistsException(Exception):
        pass

    class _Handlers:
        @winter.web.exception_handler
        @winter.web.response_status(HTTPStatus.FORBIDDEN)
        def handle(self, exception: ProblemExistsException) -> handler_return_type:  # pragma: no cover
            pass

    class _TestAPI:
        @winter.web.raises(ProblemExistsException)
        @winter.web.route_get('resource')
        def get_resource(self):  # pragma: no cover
            pass

    app = web_application(_Handlers, _TestAPI, injector=app_injector)

    # Act
    result = winter.openapi.generate_openapi(app, title='title', version='1.0.0')
    # Assert
    assert result == {
        'components': expected_components,
        'info': {'title': 'title', 'version': '1.0.0'},
        'openapi': '3.0.3',
        'paths': {
            '/resource': {
                'get': {
                    'deprecated': False,
                    'operationId': '_TestAPI.get_resource',
                    'parameters': [],
                    'responses': {
                        '200': {'description': ''},
                        '403': {**handler_spec, 'description': ''}
                    },
                    'tags': ['resource'],
                },
            },
        },
        'servers': [{'url': '/'}],
        'tags': [],
    }
