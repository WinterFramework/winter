import pytest
from django.http import QueryDict
from mock import Mock
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request as DRFRequest

from winter.core import ComponentMethod
from winter.pagination import PagePosition
from winter.pagination import PagePositionArgumentResolver


@pytest.mark.parametrize(('argument_type', 'expected_is_supported'), (
    (PagePosition, True),
    (object, False),
))
def test_is_supported_in_page_position_argument_resolver(argument_type, expected_is_supported):
    def func(arg1: argument_type):
        return arg1

    method = ComponentMethod(func)
    argument = method.get_argument('arg1')
    resolver = PagePositionArgumentResolver()

    # Act
    is_supported = resolver.is_supported(argument)

    # Assert
    assert is_supported == expected_is_supported, argument.type_


@pytest.mark.parametrize(('query_string', 'expected_page_position'), (
    ('limit=1&offset=3', PagePosition(1, 3)),
    ('limit=1', PagePosition(1)),
    ('limit=', PagePosition(None)),
    ('limit=0', PagePosition(None)),
    ('offset=3', PagePosition(None, 3)),
    ('', PagePosition(None, None)),
    ('offset=0', PagePosition(None, 0)),
))
def test_resolve_argument_ok_in_page_position_argument_resolver(query_string, expected_page_position):
    def func(arg1: int):
        return arg1

    method = ComponentMethod(func)
    argument = method.get_argument('arg1')

    resolver = PagePositionArgumentResolver()

    request = Mock(spec=DRFRequest)
    request.query_params = QueryDict(query_string)

    # Act
    page_position = resolver.resolve_argument(argument, request)

    # Assert
    assert page_position == expected_page_position


@pytest.mark.parametrize(('query_string', 'exception_type', 'message'), (
    ('limit=none', ParseError, 'Invalid "limit" query parameter value: "none"'),
    ('offset=-20', ValidationError, 'Invalid "offset" query parameter value: "-20"'),
))
def test_resolve_argument_fails_in_page_position_argument_resolver(query_string, exception_type, message):
    def func(arg1: int):
        return arg1

    method = ComponentMethod(func)
    argument = method.get_argument('arg1')

    request = Mock(spec=DRFRequest)
    request.query_params = QueryDict(query_string)
    resolver = PagePositionArgumentResolver()

    # Assert
    with pytest.raises(exception_type) as exception_info:
        # Act
        resolver.resolve_argument(argument, request)

    assert exception_info.value.args[0] == message
