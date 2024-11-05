from dataclasses import dataclass
from http import HTTPStatus

import pytest

import winter
from winter.web.routing import get_route
from winter_openapi import generate_openapi
from winter_openapi.annotations import global_exception


def test_global_exception_annotated_on_method():
    @global_exception
    class GlobalException(Exception):
        pass

    class _TestAPI:
        @winter.raises(GlobalException)
        @winter.route_get('resource')
        def get_resource(self):  # pragma: no cover
            pass

    route = get_route(_TestAPI.get_resource)
    # Act
    result = generate_openapi(
        title='title',
        version='1.0.0',
        routes=[route],
    )
    # Assert
    assert result == {
        'components': {'parameters': {}, 'responses': {}, 'schemas': {}},
        'info': {'title': 'title', 'version': '1.0.0'},
        'openapi': '3.0.4',
        'paths': {
            '/resource': {
                'get': {
                    'deprecated': False,
                    'operationId': '_TestAPI.get_resource',
                    'parameters': [],
                    'responses': {'200': {'description': ''}},
                    'tags': ['resource'],
                },
            },
        },
        'servers': [{'url': '/'}],
        'tags': [],
    }


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
def test_exception_annotated_on_method_with_custom_handler_with_dto(
    handler_return_type,
    handler_spec,
    expected_components,
):
    @winter.web.problem(status=HTTPStatus.FORBIDDEN)
    class ProblemExistsException(Exception):
        pass

    class ProblemExistsExceptionHandler(winter.web.ExceptionHandler):
        @winter.response_status(HTTPStatus.FORBIDDEN)
        def handle(self, exception: ProblemExistsException, **kwargs) -> handler_return_type:  # pragma: no cover
            pass

    class _TestAPI:
        @winter.raises(ProblemExistsException, ProblemExistsExceptionHandler)
        @winter.route_get('resource')
        def get_resource(self):  # pragma: no cover
            pass

    route = get_route(_TestAPI.get_resource)
    # Act
    result = generate_openapi(
        title='title',
        version='1.0.0',
        routes=[route],
    )
    # Assert
    assert result == {
        'components': expected_components,
        'info': {'title': 'title', 'version': '1.0.0'},
        'openapi': '3.0.4',
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
