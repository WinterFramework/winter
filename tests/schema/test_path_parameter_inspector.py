from drf_yasg import openapi

import winter
from winter.web.routing import get_route
from winter_openapi import PathParametersInspector


class ControllerForTestingInspectors:

    @winter.route_post('{valid_param}/{invalid_param}/{not_in_method}/{?query_parameter}')
    def simple_method(
            self,
            valid_param: int,
            invalid_param: object,
            query_parameter: int,
    ):
        """
        :param valid_param: Valid doc
        :param invalid_param: Invalid doc
        """
        pass


def test_path_parameter_inspector():
    inspector = PathParametersInspector()
    route = get_route(ControllerForTestingInspectors.simple_method)
    # Act
    parameters = inspector.inspect_parameters(route)

    # Assert
    assert len(parameters) == 2
    parameter_by_name = {parameter.name: parameter for parameter in parameters}
    valid_parameter = parameter_by_name['valid_param']
    assert valid_parameter.type == openapi.TYPE_INTEGER
    assert valid_parameter.description == 'Valid doc'

    invalid_parameter = parameter_by_name['invalid_param']
    assert invalid_parameter.type == openapi.TYPE_STRING
    assert invalid_parameter.description == 'Invalid doc (Note: parameter type can be wrong)'
    assert 'not_in_method' not in parameter_by_name
