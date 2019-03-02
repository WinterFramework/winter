import typing

import pytest
from django.http import HttpRequest
from django.http import QueryDict
from rest_framework.exceptions import ParseError
from rest_framework.request import Request

import winter
from winter.query_parameter import QueryParameterResolver


def get_request(query_string):
    django_request = HttpRequest()
    django_request.GET = QueryDict(query_string, mutable=True)
    return Request(django_request)


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
    assert resolver.is_supported(argument)
    assert resolver.resolve_argument(argument, request) == expected_value


@pytest.mark.parametrize(('query_string', 'expected_exception_message'), (
        ('query_param=invalid_int', 'Invalid query parameter "query_param" value "invalid_int"'),
        ('', 'Missing required query parameter "query_param"'),
))
def test_query_parameter_resolver_with_raises(query_string, expected_exception_message):
    @winter.query_parameter('query_param')
    def method(query_param: int):
        return query_param

    resolver = QueryParameterResolver()

    argument = method.get_argument('query_param')
    request = get_request(query_string)
    assert resolver.is_supported(argument)

    with pytest.raises(ParseError) as exception:
        resolver.resolve_argument(argument, request)

    assert str(exception.value) == expected_exception_message
