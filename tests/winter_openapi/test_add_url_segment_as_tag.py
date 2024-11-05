import winter
from winter.web.routing import get_route
from winter_openapi import generate_openapi


def test_add_url_segment_as_tag_false():
    class _TestAPI:
        @winter.route_get('resource')
        def get_resource(self):  # pragma: no cover
            pass

    route = get_route(_TestAPI.get_resource)
    # Act
    result = generate_openapi(
        title='title',
        version='1.0.0',
        description='description',
        routes=[route],
        add_url_segment_as_tag=False,
    )
    # Assert
    assert result == {
        'components': {'parameters': {}, 'responses': {}, 'schemas': {}},
        'info': {'description': 'description', 'title': 'title', 'version': '1.0.0'},
        'openapi': '3.0.4',
        'paths': {
            '/resource': {
                'get': {
                    'deprecated': False,
                    'operationId': '_TestAPI.get_resource',
                    'parameters': [],
                    'responses': {'200': {'description': ''}},
                    'tags': [],
                },
            },
        },
        'servers': [{'url': '/'}],
        'tags': []
    }
