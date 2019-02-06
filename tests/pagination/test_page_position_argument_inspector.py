import pytest
from mock import Mock

from winter.controller import ControllerMethod
from winter.controller import ControllerMethodArgument
from winter.pagination import PagePosition
from winter.pagination import PagePositionArgumentInspector
from winter.pagination import PagePositionArgumentResolver


@pytest.mark.parametrize(('argument_type', 'expected_count_parameters'), (
        (PagePosition, 2),
        (object, 0),
))
def test_page_position_argument_inspector(argument_type, expected_count_parameters):
    resolver = PagePositionArgumentResolver()
    inspector = PagePositionArgumentInspector(resolver)
    controller_method = Mock(spec=ControllerMethod)
    argument = Mock(spec=ControllerMethodArgument)
    argument.type_ = argument_type
    controller_method.arguments = [argument]

    # Act
    parameters = inspector.inspect_parameters(controller_method)

    # Assert
    assert len(parameters) == expected_count_parameters
