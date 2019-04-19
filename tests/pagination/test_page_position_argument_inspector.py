import pytest

import winter
from winter.pagination import PagePosition
from winter.pagination import PagePositionArgumentsInspector
from winter.pagination import PagePositionArgumentResolver
from winter.routing import get_route


@pytest.mark.parametrize(('argument_type', 'must_return_parameters'), (
    (PagePosition, True),
    (object, False),
))
def test_page_position_argument_inspector(argument_type, must_return_parameters):
    class SimpleController:
        @winter.route_get('')
        def method(arg1: argument_type):
            return arg1

    route = get_route(SimpleController.method)

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
