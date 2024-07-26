import datetime
import decimal
import uuid
from dataclasses import dataclass
from enum import Enum
from enum import IntEnum
from enum import auto
from typing import Any
from typing import Generic
from typing import List
from typing import NewType
from typing import Optional
from typing import Set
from typing import TypeVar
from typing import Union

import pytest
from strenum import StrEnum

import winter
import winter.core
from winter.core.json import Undefined
from winter.core.utils import TypeWrapper
from winter.data.pagination import Page
from winter.web.routing import get_route
from winter_openapi import generate_openapi
from winter_openapi.generator import CanNotInspectType


class IntegerValueEnum(Enum):
    RED = 1
    GREEN = 2


TestType = NewType('TestType', int)


@dataclass
class NestedDataclass:
    nested_number: int


class Id(int):
    pass


@dataclass
class Dataclass:
    """
    Parent data class description
    @param nested: doc string for nested field
    """
    nested: NestedDataclass


@dataclass
class DataclassWithOptionalField:
    """DataclassWithOptionalField description"""
    nested: Optional[NestedDataclass]


class StringValueEnum(Enum):
    RED = 'red'
    GREEN = 'green'


class StringEnum(StrEnum):
    RED = auto()
    GREEN = auto()


class MixedValueEnum(Enum):
    RED = 123
    GREEN = 'green'


class IntegerEnum(IntEnum):
    RED = 1
    GREEN = 2


class DataclassWrapper(TypeWrapper):
    pass


CustomPageItem = TypeVar('CustomPageItem')


@dataclass(frozen=True)
class CustomPage(Page, Generic[CustomPageItem]):
    extra: str


TypeVarItem = TypeVar('TypeVarItem')


@dataclass
class RequestBodyWithUndefined:
    """Some description"""
    field_a: Union[str, Undefined]
    field_b: Union[str, Undefined] = Undefined()


@pytest.mark.parametrize('type_hint, expected_response_info, expected_components', [
    (
        TestType,
        {'schema': {'format': 'int32', 'type': 'integer'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        Id,
        {'schema': {'format': 'int32', 'type': 'integer'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        uuid.UUID,
        {'schema': {'format': 'uuid', 'type': 'string'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        bool,
        {'schema': {'type': 'boolean'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        dict,
        {'schema': {'type': 'object'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        float,
        {'schema': {'format': 'float', 'type': 'number'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        decimal.Decimal,
        {'schema': {'format': 'decimal', 'type': 'string'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        Optional[int],
        {'schema': {'format': 'int32', 'type': 'integer', 'nullable': True}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        datetime.datetime,
        {'schema': {'format': 'date-time', 'type': 'string'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        datetime.date,
        {'schema': {'format': 'date', 'type': 'string'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        int,
        {'schema': {'format': 'int32', 'type': 'integer'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        str,
        {'schema': {'type': 'string'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        bytes,
        {'schema': {'format': 'bytes', 'type': 'string'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        IntegerEnum,
        {'schema': {'enum': [1, 2], 'format': 'int32', 'type': 'integer'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        IntegerValueEnum,
        {'schema': {'enum': [1, 2], 'format': 'int32', 'type': 'integer'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        StringValueEnum,
        {'schema': {'enum': ['red', 'green'], 'type': 'string'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        StringEnum,
        {'schema': {'enum': ['RED', 'GREEN'], 'type': 'string'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        MixedValueEnum,
        {'schema': {'enum': [123, 'green'], 'type': 'string'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        List[IntegerValueEnum],
        {'schema': {'items': {'enum': [1, 2], 'format': 'int32', 'type': 'integer'}, 'type': 'array'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        List[StringValueEnum],
        {'schema': {'items': {'enum': ['red', 'green'], 'type': 'string'}, 'type': 'array'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        Any,
        {
            'schema': {
                'description': 'Can be any value - string, number, boolean, array or object.',
                'nullable': False
            }
        },
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        TypeVarItem,
        {
            'schema': {
                'description': 'Can be any value - string, number, boolean, array or object.',
                'nullable': False
            }
        },
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        Optional[Any],
        {
            'schema': {
                'description': 'Can be any value - string, number, boolean, array or object.',
                'nullable': True
            }
        },
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        List,
        {
            'schema': {
                'items': {
                    'description': 'Can be any value - string, number, boolean, array or object.',
                    'nullable': False,
                },
                'type': 'array',
            },
        },
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        List[Any],
        {
            'schema': {
                'items': {
                    'description': 'Can be any value - string, number, boolean, array or object.',
                    'nullable': False,
                },
                'type': 'array',
            },
        },
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        Set[int],
        {'schema': {'items': {'format': 'int32', 'type': 'integer'}, 'type': 'array'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        Dataclass,
        {
            'schema': {
                '$ref': '#/components/schemas/Dataclass',
            },
        },
        {
            'parameters': {},
            'responses': {},
            'schemas': {
                'NestedDataclass': {
                    'description': 'NestedDataclass(nested_number: int)',
                    'properties': {'nested_number': {'format': 'int32', 'type': 'integer'}},
                    'required': ['nested_number'],
                    'title': 'NestedDataclass',
                    'type': 'object',
                },
                'Dataclass': {
                    'description': 'Parent data class description',
                    'properties': {
                        'nested': {
                            '$ref': '#/components/schemas/NestedDataclass',
                        },
                    },
                    'required': ['nested'],
                    'title': 'Dataclass',
                    'type': 'object',
                }
            },
        },
    ),
    (
        DataclassWithOptionalField,
        {
            'schema': {
                '$ref': '#/components/schemas/DataclassWithOptionalField',
            },
        },
        {
            'parameters': {},
            'responses': {},
            'schemas': {
                'NestedDataclass': {
                    'properties': {'nested_number': {'format': 'int32', 'type': 'integer'}},
                    'required': ['nested_number'],
                    'title': 'NestedDataclass',
                    'type': 'object',
                    'description': 'NestedDataclass(nested_number: int)',
                },
                'DataclassWithOptionalField': {
                    'description': 'DataclassWithOptionalField description',
                    'properties': {
                        'nested': {
                            'nullable': True,
                            'allOf': [
                                {
                                    '$ref': '#/components/schemas/NestedDataclass',
                                },
                            ],
                        },
                    },
                    'required': ['nested'],
                    'title': 'DataclassWithOptionalField',
                    'type': 'object',
                }
            },
        },
    ),
    (
        Page[NestedDataclass],
        {
            'schema': {
                '$ref': '#/components/schemas/PageOfNestedDataclass',
            },
        },
        {
            'parameters': {},
            'responses': {},
            'schemas': {
                'PageMetaOfNestedDataclass': {
                    'description': (
                        'PageMetaOfNestedDataclass(total_count: int, limit: Union[int, NoneType], '
                        'offset: Union[int, NoneType], previous: Union[str, NoneType], next: Union[str, NoneType])'
                    ),
                    'properties': {
                        'limit': {'format': 'int32', 'nullable': True, 'type': 'integer'},
                        'offset': {'format': 'int32', 'nullable': True, 'type': 'integer'},
                        'next': {'nullable': True, 'type': 'string'},
                        'previous': {'nullable': True, 'type': 'string'},
                        'total_count': {'format': 'int32', 'type': 'integer'},
                    },
                    'required': ['total_count', 'limit', 'offset', 'previous', 'next'],
                    'title': 'PageMetaOfNestedDataclass',
                    'type': 'object',
                },
                'NestedDataclass': {
                    'description': 'NestedDataclass(nested_number: int)',
                    'properties': {'nested_number': {'format': 'int32', 'type': 'integer'}},
                    'required': ['nested_number'],
                    'title': 'NestedDataclass',
                    'type': 'object',
                },
                'PageOfNestedDataclass': {
                    'description': (
                        'PageOfNestedDataclass('
                        'meta: winter_openapi.inspectors.page_inspector.PageMetaOfNestedDataclass, '
                        'objects: List[test_api_request_and_response_spec.NestedDataclass])'
                    ),
                    'properties': {
                        'meta': {
                            '$ref': '#/components/schemas/PageMetaOfNestedDataclass',
                        },
                        'objects': {
                            'items': {
                                '$ref': '#/components/schemas/NestedDataclass',
                            },
                            'type': 'array',
                        },
                    },
                    'required': ['meta', 'objects'],
                    'title': 'PageOfNestedDataclass',
                    'type': 'object',
                }
            },
        },
    ),
    (
        CustomPage[int],
        {
            'schema': {
                '$ref': '#/components/schemas/PageOfInteger',
            },
        },
        {
            'parameters': {},
            'responses': {},
            'schemas': {
                'PageMetaOfInteger': {
                    'description': (
                        'PageMetaOfInteger(total_count: int, limit: Union[int, NoneType], '
                        'offset: Union[int, NoneType], previous: Union[str, NoneType], next: Union[str, NoneType], '
                        'extra: str)'
                    ),
                    'properties': {
                        'extra': {'type': 'string'},
                        'limit': {'format': 'int32', 'nullable': True, 'type': 'integer'},
                        'offset': {'format': 'int32', 'nullable': True, 'type': 'integer'},
                        'next': {'nullable': True, 'type': 'string'},
                        'previous': {'nullable': True, 'type': 'string'},
                        'total_count': {'format': 'int32', 'type': 'integer'}},
                    'required': ['total_count', 'limit', 'offset', 'previous', 'next', 'extra'],
                    'title': 'PageMetaOfInteger',
                    'type': 'object',
                },
                'PageOfInteger': {
                    'description': (
                        'PageOfInteger(meta: winter_openapi.inspectors.page_inspector.PageMetaOfInteger, '
                        'objects: List[int])'
                    ),
                    'properties': {
                        'meta': {
                            '$ref': '#/components/schemas/PageMetaOfInteger',
                        },
                        'objects': {'items': {'format': 'int32', 'type': 'integer'}, 'type': 'array'},
                    },
                    'required': ['meta', 'objects'],
                    'title': 'PageOfInteger',
                    'type': 'object',
                }
            },
        },
    ),
    (
        DataclassWrapper[NestedDataclass],
        {
            'schema': {
                '$ref': '#/components/schemas/NestedDataclass',
            },
        },
        {
            'parameters': {},
            'responses': {},
            'schemas': {
                'NestedDataclass': {
                    'description': 'NestedDataclass(nested_number: int)',
                    'properties': {'nested_number': {'format': 'int32', 'type': 'integer'}},
                    'required': ['nested_number'],
                    'title': 'NestedDataclass',
                    'type': 'object',
                }
            },
        },
    ),
])
def test_response_return_type(type_hint, expected_response_info, expected_components):
    class _TestAPI:
        @winter.route_get('/types/')
        def simple_method(self) -> type_hint:  # pragma: no cover
            pass

    route = get_route(_TestAPI.simple_method)
    expected_method_info = {
        'deprecated': False,
        'operationId': '_TestAPI.simple_method',
        'parameters': [],
        'responses': {
            '200': {
                'content': {
                    'application/json': expected_response_info,
                },
                'description': '',
            },
        },
        'tags': ['types'],
    }
    # Act
    result = generate_openapi(title='title', version='1.0.0', routes=[route])

    # Assert
    method_info = result['paths']['/types/']['get']
    assert method_info == expected_method_info, type_hint
    assert result['components'] == expected_components


def test_response_with_invalid_return_type():
    class _TestAPI:
        @winter.route_get('')
        def with_invalid_return_type(self) -> object:  # pragma: no cover
            pass

    route = get_route(_TestAPI.with_invalid_return_type)

    with pytest.raises(CanNotInspectType) as e:
        # Act
        generate_openapi(title='title', version='1.0.0', routes=[route])

    assert repr(e.value) == (
        "CanNotInspectType(test_api_request_and_response_spec._TestAPI.with_invalid_return_type: "
        "Unknown type: <class 'object'>)"
    )


@pytest.mark.parametrize('type_hint, expected_request_body_spec, expected_components', [
    (
        List[IntegerValueEnum],
        {'schema': {'items': {'enum': [1, 2], 'format': 'int32', 'type': 'integer'}, 'type': 'array'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        List[StringValueEnum],
        {'schema': {'items': {'enum': ['red', 'green'], 'type': 'string'}, 'type': 'array'}},
        {'parameters': {}, 'responses': {}, 'schemas': {}},
    ),
    (
        Dataclass,
        {
            'schema': {
                '$ref': '#/components/schemas/DataclassInput',
            },
        },
        {
            'parameters': {},
            'responses': {},
            'schemas': {
                'NestedDataclassInput': {
                    'description': 'NestedDataclass(nested_number: int)',
                    'properties': {'nested_number': {'format': 'int32', 'type': 'integer'}},
                    'required': ['nested_number'],
                    'title': 'NestedDataclassInput',
                    'type': 'object',
                },
                'DataclassInput': {
                    'description': 'Parent data class description',
                    'properties': {
                        'nested': {
                            '$ref': '#/components/schemas/NestedDataclassInput',
                        },
                    },
                    'required': ['nested'],
                    'title': 'DataclassInput',
                    'type': 'object',
                },
            },
        },
    ),
    (
        RequestBodyWithUndefined,
        {
            'schema': {
                '$ref': '#/components/schemas/RequestBodyWithUndefinedInput',
            },
        },
        {
            'parameters': {},
            'responses': {},
            'schemas': {
                'RequestBodyWithUndefinedInput': {
                    'title': 'RequestBodyWithUndefinedInput',
                    'description': 'Some description',
                    'type': 'object',
                    'properties': {
                        'field_a': {'type': 'string'},
                        'field_b': {'type': 'string'},
                    },
                },
            },
        },
    ),
])
def test_request_type(type_hint, expected_request_body_spec, expected_components):
    class _TestAPI:
        @winter.route_post('/types/')
        @winter.request_body('data')
        def simple_method(self, data: type_hint):  # pragma: no cover
            pass

    route = get_route(_TestAPI.simple_method)

    # Act
    result = generate_openapi(title='title', version='1.0.0', routes=[route])

    # Assert
    method_info = result['paths']['/types/']['post']['requestBody']
    assert method_info == {'content': {'application/json': expected_request_body_spec}, 'required': False}
    assert result['components'] == expected_components


def test_reuse_schema():
    class _TestAPI:  # pragma: no cover
        @winter.route_get('/method_1/')
        def method_1(self) -> Dataclass:
            pass

        @winter.route_get('/method_2/')
        def method_2(self) -> Dataclass:
            pass

        @winter.route_post('/method_3/')
        @winter.request_body('data')
        def method_3(self, data: Dataclass):
            pass

        @winter.route_post('/method_4/')
        @winter.request_body('data')
        def method_4(self, data: Dataclass):
            pass

    result = generate_openapi(
        title='title',
        version='1.0.0',
        routes=[
            get_route(_TestAPI.method_1),
            get_route(_TestAPI.method_2),
            get_route(_TestAPI.method_3),
            get_route(_TestAPI.method_4),
        ],
    )
    assert result == {
        'components': {
            'parameters': {},
            'responses': {},
            'schemas': {
                'NestedDataclass': {
                    'description': 'NestedDataclass(nested_number: int)',
                    'properties': {
                        'nested_number': {
                            'format': 'int32',
                            'type': 'integer',
                        },
                    },
                    'required': ['nested_number'],
                    'title': 'NestedDataclass',
                    'type': 'object',
                },
                'NestedDataclassInput': {
                    'description': 'NestedDataclass(nested_number: int)',
                    'properties': {
                        'nested_number': {
                            'format': 'int32',
                            'type': 'integer',
                        },
                    },
                    'required': ['nested_number'],
                    'title': 'NestedDataclassInput',
                    'type': 'object',
                },
                'Dataclass': {
                    'description': 'Parent data class description',
                    'properties': {
                        'nested': {
                            '$ref': '#/components/schemas/NestedDataclass',
                        },
                    },
                    'required': ['nested'],
                    'title': 'Dataclass',
                    'type': 'object',
                },
                'DataclassInput': {
                    'description': 'Parent data class description',
                    'properties': {
                        'nested': {
                            '$ref': '#/components/schemas/NestedDataclassInput',
                        },
                    },
                    'required': ['nested'],
                    'title': 'DataclassInput',
                    'type': 'object',
                },
            },
        },
        'info': {'title': 'title', 'version': '1.0.0'},
        'openapi': '3.0.3',
        'paths': {
            '/method_1/': {
                'get': {
                    'deprecated': False,
                    'operationId': '_TestAPI.method_1',
                    'parameters': [],
                    'responses': {
                        '200': {
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': '#/components/schemas/Dataclass'},
                                },
                            },
                            'description': '',
                        },
                    },
                    'tags': ['method_1'],
                },
            },
            '/method_2/': {
                'get': {
                    'deprecated': False,
                    'operationId': '_TestAPI.method_2',
                    'parameters': [],
                    'responses': {
                        '200': {
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': '#/components/schemas/Dataclass'},
                                },
                            },
                            'description': '',
                        },
                    },
                    'tags': ['method_2'],
                },
            },
            '/method_3/': {
                'post': {
                    'deprecated': False,
                    'operationId': '_TestAPI.method_3',
                    'parameters': [],
                    'requestBody': {
                        'content': {
                            'application/json': {
                                'schema': {'$ref': '#/components/schemas/DataclassInput'},
                            },
                        },
                        'required': False,
                    },
                    'responses': {
                        '200': {'description': ''},
                    },
                    'tags': ['method_3'],
                },
            },
            '/method_4/': {
                'post': {
                    'deprecated': False,
                    'operationId': '_TestAPI.method_4',
                    'parameters': [],
                    'requestBody': {
                        'content': {
                            'application/json': {
                                'schema': {'$ref': '#/components/schemas/DataclassInput'},
                            },
                        },
                        'required': False
                    },
                    'responses': {
                        '200': {'description': ''},
                    },
                    'tags': ['method_4'],
                },
            },
        },
        'servers': [{'url': '/'}],
        'tags': [],
    }


def test_raises_for_type_duplicates():
    class DuplicateTypes:
        @dataclass
        class Dataclass:
            nested: NestedDataclass

    class _TestAPI:  # pragma: no cover
        @winter.route_get('/method_1/')
        def method_1(self) -> Dataclass:
            pass

        @winter.route_get('/method_2/')
        def method_2(self) -> DuplicateTypes.Dataclass:
            pass

    with pytest.raises(ValueError) as e:
        generate_openapi(
            title='title',
            version='1.0.0',
            routes=[
                get_route(_TestAPI.method_1),
                get_route(_TestAPI.method_2),
            ],
        )

    assert str(e.value) == (
        'Title Dataclass for type '
        "<class 'test_api_request_and_response_spec.test_raises_for_type_duplicates.<locals>.DuplicateTypes.Dataclass'>"
        " is already used for another type: <class 'test_api_request_and_response_spec.Dataclass'>"
    )
