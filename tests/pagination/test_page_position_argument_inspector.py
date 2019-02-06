import pytest

from winter.controller import ControllerMethod
from winter.pagination import PagePosition
from winter.pagination import PagePositionArgumentInspector
from winter.pagination import PagePositionArgumentResolver


@pytest.mark.parametrize(('argument_type', 'must_return_parameters'), (
        (PagePosition, True),
        (object, False),
))
def test_page_position_argument_inspector(argument_type, must_return_parameters):
    def func(arg1: argument_type):
        return arg1

    controller_method = ControllerMethod(func, '/', 'GET')
    resolver = PagePositionArgumentResolver()
    inspector = PagePositionArgumentInspector(resolver)

    if must_return_parameters:
        expected_parameters = [
            inspector.limit_parameter,
            inspector.offset_parameter,
        ]
    else:
        expected_parameters = []

    # Act
    parameters = inspector.inspect_parameters(controller_method)

    # Assert
    assert parameters == expected_parameters
