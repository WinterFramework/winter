from typing import List
from typing import Optional

import pytest
from dateutil import parser
from rest_framework.test import APIClient
from uritemplate import URITemplate

import winter
from tests.entities import AuthorizedUser
from tests.utils import get_request
from winter.core.annotations import AlreadyAnnotated
from winter.core.json import decoder
from winter.web.argument_resolver import ArgumentNotSupported
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
    ):
        return without_default, optional, array, with_default

    resolver = QueryParameterArgumentResolver()

    argument = method.get_argument(argument_name)
    request = get_request(query_string)
    assert resolver.resolve_argument(argument, request, {}) == expected_value


@pytest.mark.parametrize(
    ('query_string', 'expected_exception_message'), (
        ('query_param=invalid_int', 'Cannot decode "invalid_int" to integer'),
        ('', 'Missing required query parameter "query_param"'),
    ),
)
def test_query_parameter_resolver_with_raises_parse_error(query_string, expected_exception_message):
    @winter.route_get('{?query_param}')
    def method(query_param: int):
        return query_param

    resolver = QueryParameterArgumentResolver()

    argument = method.get_argument('query_param')
    request = get_request(query_string)

    with pytest.raises(decoder.JSONDecodeException) as exception:
        resolver.resolve_argument(argument, request, {})

    assert str(exception.value) == expected_exception_message


@pytest.mark.parametrize(
    ('argument_name', 'expected_is_supported'), (
        ('query_param', True),
        ('invalid_query_param', False),
    ),
)
def test_is_supported(argument_name, expected_is_supported):
    @winter.route_get('{?' + argument_name + '}')
    def method(query_param: int):
        return query_param

    resolver = QueryParameterArgumentResolver()

    argument = method.get_argument('query_param')
    is_supported = resolver.is_supported(argument)
    second_is_supported = resolver.is_supported(argument)

    assert is_supported == second_is_supported == expected_is_supported


def test_query_parameter_resolver_with_raises_argument_not_supported():

    @winter.route_get()
    def method(invalid_query_param: int):
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
        def method(query_param: int):
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
        def method(query_param: int):
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
    def method(x_param: int, y_param: int = 1):
        return 0

    resolver = QueryParameterArgumentResolver()

    argument = method.get_argument('x_param')
    request = get_request('?x=1')

    with pytest.raises(decoder.JSONDecodeException) as exception:
        resolver.resolve_argument(argument, request, {})

    assert str(exception.value) == 'Missing required query parameter "x"'


@pytest.mark.parametrize(
    ('date', 'date_time', 'boolean', 'optional_boolean', 'array', 'string'), (
        ('2019-05-02', '2019-05-02 22:28:31', 'false', None, [10, 20], 'xyz'),
        ('2019-05-01', '2019-05-01 22:28:31', 'true', 'true', [10, 20], 'xyz'),
        ('2019-05-01', '2019-05-01 22:28:31', 'true', 'false', [10, 20], 'xyz'),
    ),
)
def test_query_parameter(date, date_time, boolean, optional_boolean, array, string):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    expected_data = {
        'date': parser.parse(date).date(),
        'date_time': parser.parse(date_time),
        'boolean': boolean == 'true',
        'optional_boolean': optional_boolean == 'true' if optional_boolean is not None else None,
        'array': array,
        'expanded_array': list(map(str, array)),
        'string': string,
    }
    base_uri = URITemplate(
        '/with-query-parameter/'
        '{?date,date_time,boolean,optional_boolean,array,expanded_array*,string}',
    )
    query_params = {
        'date': date,
        'date_time': date_time,
        'boolean': boolean,
        'array': ','.join(map(str, array)),
        'expanded_array': array,
        'string': string,
    }

    if optional_boolean is not None:
        query_params['optional_boolean'] = optional_boolean

    base_uri = base_uri.expand(**query_params)

    # Act
    http_response = client.get(base_uri)
    assert http_response.data == expected_data
