import pytest
from drf_yasg import openapi

import winter
from winter.data.pagination import PagePosition
from winter_openapi import PagePositionArgumentsInspector
from winter.web.pagination import PagePositionArgumentResolver
from winter.web.routing import get_route


@pytest.mark.parametrize(('argument_type', 'must_return_parameters'), (
    (PagePosition, True),
    (object, False),
))
def test_page_position_argument_inspector(argument_type, must_return_parameters):
    class TestAPI:
        @winter.route_get('')
        def method(self, arg1: argument_type):  # pragma: no cover
            pass

    route = get_route(TestAPI.method)

    resolver = PagePositionArgumentResolver()
    inspector = PagePositionArgumentsInspector(resolver)

    if must_return_parameters:
        expected_parameters = [
            inspector.limit_parameter,
            inspector.offset_parameter,
        ]
    else:
        expected_parameters = []

    # Act
    parameters = inspector.inspect_parameters(route)

    # Assert
    assert parameters == expected_parameters


@pytest.mark.parametrize(('default_sort', 'default_in_parameter'), ((None, None), (('id',), 'id')))
def test_page_position_argument_inspector_with_allowed_order_by_fields(default_sort, default_in_parameter):

    class TestAPI:
        @winter.route_get('')
        @winter.web.pagination.order_by(['id'], default_sort=default_sort)
        def method(self, arg1: PagePosition):  # pragma: no cover
            pass

    route = get_route(TestAPI.method)

    resolver = PagePositionArgumentResolver()
    inspector = PagePositionArgumentsInspector(resolver)

    order_by_parameter = openapi.Parameter(
        name=resolver.order_by_name,
        description='Comma separated order by fields. Allowed fields: id.',
        required=False,
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_ARRAY,
        items={'type': openapi.TYPE_STRING},
        default=default_in_parameter,
    )

    expected_parameters = [
        inspector.limit_parameter,
        inspector.offset_parameter,
        order_by_parameter,
    ]

    # Act
    parameters = inspector.inspect_parameters(route)

    # Assert
    assert parameters == expected_parameters
