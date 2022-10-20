import pytest
from django.http import QueryDict
from mock import Mock
from rest_framework.exceptions import ParseError
from rest_framework.request import Request as DRFRequest

import winter
from winter.core import ComponentMethod
from winter.core.json import decoder
from winter.data.pagination import PagePosition
from winter.data.pagination import Sort
from winter.web.exceptions import RequestDataDecodeException
from winter.web.pagination import PagePositionArgumentResolver


@pytest.mark.parametrize(
    ('argument_type', 'expected_is_supported'), (
        (PagePosition, True),
        (object, False),
    ),
)
def test_is_supported_in_page_position_argument_resolver(argument_type, expected_is_supported):
    def func(arg1: argument_type):  # pragma: no cover
        return arg1

    method = ComponentMethod(func)
    argument = method.get_argument('arg1')
    resolver = PagePositionArgumentResolver()

    # Act
    is_supported = resolver.is_supported(argument)

    # Assert
    assert is_supported == expected_is_supported, argument.type_


def test_resolve_argument_with_order_by_without_order_by_annotation():
    @winter.core.component_method
    def method(arg1: PagePosition):  # pragma: no cover
        return arg1

    argument = method.get_argument('arg1')
    resolver = PagePositionArgumentResolver()
    request = Mock(spec=DRFRequest)
    request.query_params = QueryDict('order_by=id')

    # Act
    page_position = resolver.resolve_argument(argument, request, {})

    # Assert
    assert page_position == PagePosition()


@pytest.mark.parametrize(
    ('query_string', 'expected_page_position'), (
        ('limit=1&offset=3', PagePosition(1, 3)),
        ('limit=1', PagePosition(1)),
        ('limit=', PagePosition(None)),
        ('limit=0', PagePosition(None)),
        ('offset=3', PagePosition(None, 3)),
        ('', PagePosition(None, None)),
        ('offset=0', PagePosition(None, 0)),
        ('limit=10&offset=20&order_by=-id,name', PagePosition(10, 20, Sort.by('id').desc().and_(Sort.by('name')))),
        ('order_by=', PagePosition(None, None)),
    ),
)
def test_resolve_argument_ok_in_page_position_argument_resolver(query_string, expected_page_position):
    @winter.web.pagination.order_by(['name', 'id', 'email', 'x'])
    def method(page_position: PagePosition):  # pragma: no cover
        return page_position

    argument = method.get_argument('page_position')

    resolver = PagePositionArgumentResolver(allow_any_order_by_field=True)

    request = Mock(spec=DRFRequest)
    request.query_params = QueryDict(query_string)

    # Act
    page_position = resolver.resolve_argument(argument, request, {})

    # Assert
    assert page_position == expected_page_position


@pytest.mark.parametrize(
    ('query_string', 'default_sort', 'expected_page_position'), (
        ('limit=1&offset=3', ('-name',), PagePosition(1, 3, Sort.by('name').desc())),
    ),
)
def test_resolve_argument_ok_in_page_position_argument_resolver_with_default(
    query_string,
    default_sort,
    expected_page_position,
):
    @winter.web.pagination.order_by(['name', 'id', 'email'], default_sort=default_sort)
    def method(page_position: PagePosition):  # pragma: no cover
        return page_position

    argument = method.get_argument('page_position')

    resolver = PagePositionArgumentResolver(allow_any_order_by_field=True)

    request = Mock(spec=DRFRequest)
    request.query_params = QueryDict(query_string)

    # Act
    page_position = resolver.resolve_argument(argument, request, {})

    # Assert
    assert page_position == expected_page_position


@pytest.mark.parametrize(
    ('query_string', 'exception_type', 'message', 'errors_dict'), (
        (
            'limit=none',
            RequestDataDecodeException,
            'Failed to decode request data',
            {'error': 'Cannot decode "none" to PositiveInteger'}
        ),
        (
            'offset=-20',
            RequestDataDecodeException,
            'Failed to decode request data',
            {'error': 'Cannot decode "-20" to PositiveInteger'}
        ),
        ('order_by=id,', ParseError, 'Invalid field for order: ""', None),
        ('order_by=-', ParseError, 'Invalid field for order: "-"', None),
        (
            'order_by=not_allowed_order_by_field',
            ParseError,
            'Fields do not allowed as order by fields: "not_allowed_order_by_field"',
            None,
        ),
    ),
)
def test_resolve_argument_fails_in_page_position_argument_resolver(query_string, exception_type, message, errors_dict):
    @winter.web.pagination.order_by(['id'])
    def method(arg1: int):  # pragma: no cover
        return arg1

    argument = method.get_argument('arg1')

    request = Mock(spec=DRFRequest)
    request.query_params = QueryDict(query_string)
    resolver = PagePositionArgumentResolver()

    # Assert
    with pytest.raises(exception_type) as exception_info:
        # Act
        resolver.resolve_argument(argument, request, {})

    assert exception_info.value.args[0] == message
    assert not hasattr(exception_info.value, 'errors') or exception_info.value.errors == errors_dict
