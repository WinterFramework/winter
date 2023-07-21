import datetime
from http import HTTPStatus
from typing import List
from typing import Optional
from uuid import UUID
from uuid import uuid4

import pytest
from uritemplate import URITemplate

import winter
from tests.utils import get_request
from winter.core.annotations import AlreadyAnnotated
from winter.web.argument_resolver import ArgumentNotSupported
from winter.web.exceptions import RequestDataDecodeException
from winter.web.query_parameters.query_parameters_argument_resolver import QueryParameterArgumentResolver


@pytest.mark.parametrize(
    ('argument_name', 'query_string', 'expected_value'), (
        ('without_default', 'without_default=1', 1),
        ('optional', 'optional=value', 'value'),
        ('optional', '', None),
        ('with_default', 'with_default=value', 'value'),
        ('with_default', '', 'default'),
        ('array', 'array=1&array=2', [1, 2]),
    ),
)
def test_query_parameter_resolver(argument_name, query_string, expected_value):
    @winter.route_get('{?without_default,optional,with_default,array*}')
    def method(
        without_default: int,
        optional: Optional[str],
        array: List[int],
        with_default: str = 'default',
    ):  # pragma: no cover
        return without_default, optional, array, with_default

    resolver = QueryParameterArgumentResolver()

    argument = method.get_argument(argument_name)
    request = get_request(query_string)
    assert resolver.resolve_argument(argument, request, {}) == expected_value


@pytest.mark.parametrize(
    ('query_string', 'expected_exception_message', 'expected_errors'), (
        (
            'query_param=invalid_int',
            'Failed to decode request data',
            {'error': 'Cannot decode "invalid_int" to integer'}
        ),
        ('', 'Failed to decode request data', {'error': 'Missing required query parameter "query_param"'}),
    ),
)
def test_query_parameter_resolver_with_raises_parse_error(query_string, expected_exception_message, expected_errors):
    @winter.route_get('{?query_param}')
    def method(query_param: int):  # pragma: no cover
        return query_param

    resolver = QueryParameterArgumentResolver()

    argument = method.get_argument('query_param')
    request = get_request(query_string)

    with pytest.raises(RequestDataDecodeException) as exception_info:
        resolver.resolve_argument(argument, request, {})

    assert str(exception_info.value) == expected_exception_message
    assert exception_info.value.errors == expected_errors


def test_query_parameter_resolver_with_raises_parse_uuid_error():
    @winter.route_get('{?query_param}')
    def method(query_param: UUID):  # pragma: no cover
        pass

    resolver = QueryParameterArgumentResolver()

    argument = method.get_argument('query_param')
    request = get_request('query_param=invalid_uuid')

    with pytest.raises(RequestDataDecodeException) as exception_info:
        resolver.resolve_argument(argument, request, {})

    assert str(exception_info.value) == 'Failed to decode request data'
    assert exception_info.value.errors == {'error': 'Cannot decode "invalid_uuid" to uuid'}


@pytest.mark.parametrize(
    ('argument_name', 'expected_is_supported'), (
        ('query_param', True),
        ('invalid_query_param', False),
    ),
)
def test_is_supported(argument_name, expected_is_supported):
    @winter.route_get('{?' + argument_name + '}')
    def method(query_param: int):  # pragma: no cover
        return query_param

    resolver = QueryParameterArgumentResolver()

    argument = method.get_argument('query_param')
    is_supported = resolver.is_supported(argument)
    second_is_supported = resolver.is_supported(argument)

    assert is_supported == second_is_supported == expected_is_supported


def test_query_parameter_resolver_with_raises_argument_not_supported():
    @winter.route_get()
    def method(invalid_query_param: int):  # pragma: no cover
        return invalid_query_param

    resolver = QueryParameterArgumentResolver()
    request = get_request('invalid_query_param=1')

    argument = method.get_argument('invalid_query_param')

    with pytest.raises(ArgumentNotSupported) as exception:
        resolver.resolve_argument(argument, request, {})

    assert str(exception.value) == 'Unable to resolve argument invalid_query_param: int'


def test_duplicate_routing_map_to():
    with pytest.raises(AlreadyAnnotated) as exception:
        @winter.map_query_parameter('y', to='query_param')
        @winter.map_query_parameter('x', to='query_param')
        def method(query_param: int):  # pragma: no cover
            return query_param
    message = (
        "Cannot annotate twice: <class 'winter.web.query_parameters."
        "map_query_parameter_annotation.MapQueryParameterAnnotation'>"
    )
    assert str(exception.value) == message


def test_duplicate_map_query_parameter_map_to():
    with pytest.raises(AlreadyAnnotated) as exception:
        @winter.map_query_parameter('x', to='query_param1')
        @winter.map_query_parameter('x', to='query_param2')
        @winter.route_get('{?query_param}')
        def method(query_param: int):  # pragma: no cover
            return query_param

    message = (
        "Cannot annotate twice: <class 'winter.web.query_parameters."
        "map_query_parameter_annotation.MapQueryParameterAnnotation'>"
    )
    assert str(exception.value) == message


def test_orphan_map_query_parameter_fails():
    @winter.route_get('{?x,y}')
    @winter.map_query_parameter('x', to='x_param')
    @winter.map_query_parameter('y', to='y_param')
    def method(x_param: int, y_param: int = 1):  # pragma: no cover
        return 0

    resolver = QueryParameterArgumentResolver()

    argument = method.get_argument('x_param')
    request = get_request('?x=1')

    with pytest.raises(RequestDataDecodeException) as exception_info:
        resolver.resolve_argument(argument, request, {})

    assert str(exception_info.value) == 'Failed to decode request data'
    assert exception_info.value.errors == {'error': 'Missing required query parameter "x"'}


@pytest.mark.parametrize(
    ('date', 'date_time', 'boolean', 'optional_boolean', 'array', 'string', 'uid'), (
        ('2019-05-02', '2019-05-01 22:28:31', 'false', None, [10, 20], 'xyz', uuid4()),
        ('2019-05-01', '2019-05-01 22:28:31', 'true', 'true', [10, 20], 'xyz', uuid4()),
        ('2019-05-01', '2019-05-01 22:28:31', 'true', 'false', [10, 20], 'xyz', uuid4()),
    ),
)
def test_query_parameter(api_client, date, date_time, boolean, optional_boolean, array, string, uid):
    expected_data = {
        'date': date,
        'date_time': '2019-05-01T22:28:31',
        'boolean': boolean == 'true',
        'optional_boolean': optional_boolean == 'true' if optional_boolean is not None else None,
        'array': array,
        'expanded_array': list(map(str, array)),
        'string': string,
        'uid': str(uid),
    }
    base_uri = URITemplate(
        '/with-query-parameter/'
        '{?date,date_time,boolean,optional_boolean,array,expanded_array*,string,uid}',
    )
    query_params = {
        'date': date,
        'date_time': date_time,
        'boolean': boolean,
        'array': ','.join(map(str, array)),
        'expanded_array': array,
        'string': string,
        'uid': uid,
    }

    if optional_boolean is not None:
        query_params['optional_boolean'] = optional_boolean

    base_uri = base_uri.expand(**query_params)

    # Act
    http_response = api_client.get(base_uri)
    assert http_response.json() == expected_data


def test_invalid_uuid_query_parameter_triggers_400(api_client):
    base_uri = URITemplate(
        '/with-query-parameter/'
        '{?date,date_time,boolean,optional_boolean,array,expanded_array*,string,uid}',
    )
    query_params = {
        'date': datetime.datetime.now().date(),
        'date_time': datetime.datetime.now(),
        'boolean': 'true',
        'array': '5',
        'expanded_array': ['5'],
        'string': '',
        'uid': str(uuid4()) + 'a',
    }

    base_uri = base_uri.expand(**query_params)

    # Act
    http_response = api_client.get(base_uri)
    assert http_response.status_code == HTTPStatus.BAD_REQUEST
