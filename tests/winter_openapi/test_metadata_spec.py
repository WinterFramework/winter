import winter
from winter.web.routing import get_route
from winter_openapi import generate_openapi


def test_generate_openapi_with_all_args_spec():
    class _TestAPI:
        @winter.route_get('resource')
        def get_resource(self):  # pragma: no cover
            pass

    route = get_route(_TestAPI.get_resource)
    tags = [{'name': 'tag_value'}]
    servers = [{'url': 'https://api.example.com/v1'}]
    # Act
    result = generate_openapi(
        title='title',
        version='1.0.0',
        description='description',
        routes=[route],
        tags=tags,
        servers=servers,
    )
    # Assert
    assert result == {
        'components': {'parameters': {}, 'responses': {}, 'schemas': {}},
        'info': {'description': 'description', 'title': 'title', 'version': '1.0.0'},
        'openapi': '3.0.3',
        'paths': {
            'resource': {
                'get': {
                    'deprecated': False,
                    'operationId': '_TestAPI.get_resource',
                    'parameters': [],
                    'responses': {'200': {'description': ''}},
                    'tags': ['tag_value', 'resource'],
                },
            },
        },
        'servers': [{'url': 'https://api.example.com/v1'}],
        'tags': [{'name': 'tag_value'}]
    }
