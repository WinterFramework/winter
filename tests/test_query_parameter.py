import typing

import pytest
from dateutil import parser
from rest_framework.exceptions import ParseError
from rest_framework.test import APIClient
from uritemplate import URITemplate

import winter
from tests.entities import AuthorizedUser
from winter.argument_resolver import ArgumentNotSupported
from winter.core import ComponentMethod
from winter.query_parameter import QueryParameterResolver
from .utils import get_request


@pytest.mark.parametrize(('argument_name', 'query_string', 'expected_value'), (
    ('without_default', 'without_default=1', 1),
    ('optional', 'optional=value', 'value'),
    ('optional', '', None),
    ('with_default', 'with_default=value', 'value'),
    ('with_default', '', 'default'),
    ('array', 'array=1&array=2', [1, 2]),
))
def test_query_parameter_resolver(argument_name, query_string, expected_value):
    @winter.query_parameter('without_default')
    @winter.query_parameter('optional')
    @winter.query_parameter('with_default')
    @winter.query_parameter('array')
    def method(
            without_default: int,
            optional: typing.Optional[str],
            array: typing.List[int],
            with_default: str = 'default',
    ):
        return without_default, optional, array, with_default

    resolver = QueryParameterResolver()

    argument = method.get_argument(argument_name)
    request = get_request(query_string)
    assert resolver.resolve_argument(argument, request) == expected_value


@pytest.mark.parametrize(('query_string', 'expected_exception_message'), (
    ('query_param=invalid_int', 'Invalid query parameter "query_param" value "invalid_int"'),
    ('', 'Missing required query parameter "query_param"'),
))
def test_query_parameter_resolver_with_raises_parse_error(query_string, expected_exception_message):
    @winter.query_parameter('query_param')
    def method(query_param: int):
        return query_param

    resolver = QueryParameterResolver()

    argument = method.get_argument('query_param')
    request = get_request(query_string)

    with pytest.raises(ParseError) as exception:
        resolver.resolve_argument(argument, request)

    assert str(exception.value) == expected_exception_message


@pytest.mark.parametrize(('argument_name', 'expected_is_supported'), (
    ('query_param', True),
    ('invalid_query_param', False),
))
def test_is_supported(argument_name, expected_is_supported):
    @winter.query_parameter(argument_name)
    def method(query_param: int):
        return query_param

    resolver = QueryParameterResolver()

    argument = method.get_argument('query_param')
    is_supported = resolver.is_supported(argument)
    second_is_supported = resolver.is_supported(argument)

    assert is_supported == second_is_supported == expected_is_supported


def test_query_parameter_resolver_with_raises_argument_not_supported():
    def method(invalid_query_param: int):
        return invalid_query_param

    method = ComponentMethod(method)

    resolver = QueryParameterResolver()
    request = get_request('invalid_query_param=1')

    argument = method.get_argument('invalid_query_param')

    with pytest.raises(ArgumentNotSupported) as exception:
        resolver.resolve_argument(argument, request)

    assert str(exception.value) == 'Unable to resolve argument invalid_query_param: int'


@pytest.mark.parametrize(('date', 'date_time', 'boolean', 'optional_boolean'), (
    ('2019-05-02', '2019-05-02 22:28:31', 'false', None),
    ('2019-05-02', '2019-05-02 22:28:31', 'false', ''),
    ('2019-05-01', '2019-05-01 22:28:31', 'true', 'true'),
    ('2019-05-01', '2019-05-01 22:28:31', 'true', 'false'),
))
def test_query_parameter(date, date_time, boolean, optional_boolean):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    expected_date = {
        'date': parser.parse(date).date(),
        'date_time': parser.parse(date_time),
        'boolean': boolean == 'true',
        'optional_boolean': optional_boolean == 'true' if optional_boolean is not None else None,
    }
    base_uri = URITemplate('/with-query-parameter/{?date,date_time,boolean,optional_boolean}')
    query_params = {
        'date': date,
        'date_time': date_time,
        'boolean': boolean,
    }

    if optional_boolean is not None:
        query_params['optional_boolean'] = optional_boolean

    base_uri = base_uri.expand(**query_params)

    # Act
    http_response = client.get(base_uri)
    assert http_response.data == expected_date
