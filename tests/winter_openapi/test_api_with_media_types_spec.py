from dataclasses import dataclass

import winter
from winter.web import MediaType
from winter.web.routing import get_route
from winter_openapi import generate_openapi


def test_generate_spec_for_media_type_produces():
    class _TestAPI:
        @winter.route_get('xml/', produces=(MediaType.APPLICATION_XML,))
        def get_xml(self) -> str:  # pragma: no cover
            return 'Hello, sir!'

    route = get_route(_TestAPI.get_xml)

    # Act
    result = generate_openapi(title='title', version='1.0.0', routes=[route])

    # Assert
    paths = result['paths']
    assert paths == {
        'xml/': {
            'get': {
                'deprecated': False,
                'operationId': '_TestAPI.get_xml',
                'parameters': [],
                'responses': {
                    '200': {
                        'content': {'application/xml': {'schema': {'type': 'string'}}},
                        'description': '',
                    },
                },
                'tags': ['xml'],
            },
        },
    }


def test_generate_spec_for_media_type_consumes():
    @dataclass
    class Data:
        field1: str

    class _TestAPI:
        @winter.route_post('xml/', consumes=(MediaType.APPLICATION_XML,))
        @winter.request_body('body')
        def get_xml(self, body: Data):  # pragma: no cover
            pass

    route = get_route(_TestAPI.get_xml)

    # Act
    result = generate_openapi(title='title', version='1.0.0', routes=[route])

    # Assert
    paths = result['paths']
    assert paths == {
        'xml/': {
            'post': {
                'deprecated': False,
                'operationId': '_TestAPI.get_xml',
                'parameters': [],
                'requestBody': {
                    'content': {
                        'application/xml': {
                            'schema': {
                                'description': 'Data(field1: str)',
                                'properties': {'field1': {'type': 'string'}},
                                'required': ['field1'],
                                'title': 'DataInput',
                                'type': 'object',
                            },
                        },
                    },
                    'required': False,
                },
                'responses': {'200': {'description': ''}},
                'tags': ['xml'],
            },
        },
    }
