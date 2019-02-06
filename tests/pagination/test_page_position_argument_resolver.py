import pytest
from django.http import QueryDict
from mock import Mock
from rest_framework.exceptions import ParseError
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request as DRFRequest

from winter.controller import ControllerMethodArgument
from winter.pagination import PagePosition
from winter.pagination import PagePositionArgumentResolver


@pytest.mark.parametrize(('type_', 'expected_is_supported'), (
        (PagePosition, True),
        (object, True),
))
def test_is_supported_in_page_position_argument_resolver(type_, expected_is_supported):
    resolver = PagePositionArgumentResolver()
    argument = Mock(spec=ControllerMethodArgument)
    argument.type_ = PagePosition

    # Act
    is_supported = resolver.is_supported(argument)

    # Assert
    assert is_supported == expected_is_supported


@pytest.mark.parametrize(('query_string', 'expected_page_position'), (
        ('limit=1&offset=3', PagePosition(1, 3)),
        ('limit=1', PagePosition(1)),
        ('offset=3', PagePosition(None, 3)),
        ('', PagePosition()),
))
def test_resolve_argument_in_page_position_argument_resolver(query_string, expected_page_position):
    resolver = PagePositionArgumentResolver()
    argument = Mock(spec=ControllerMethodArgument)

    request = Mock(spec=DRFRequest)
    request.query_params = QueryDict(query_string)

    page_position = resolver.resolve_argument(argument, request)
    assert page_position == expected_page_position


@pytest.mark.parametrize(('query_string', 'exception_type', 'message'), (
        ('limit=none', ParseError, 'Invalid "limit" query parameter value: "none"'),
        ('offset=-20', ValidationError, 'Invalid "offset" query parameter value: "-20"'),
))
def test_resolve_argument_in_page_position_argument_resolver_with_raises(query_string, exception_type, message):
    resolver = PagePositionArgumentResolver()
    argument = Mock(spec=ControllerMethodArgument)

    request = Mock(spec=DRFRequest)
    request.query_params = QueryDict(query_string)
    with pytest.raises(exception_type) as exception_info:
        resolver.resolve_argument(argument, request)
    assert exception_info.value.args[0] == message
