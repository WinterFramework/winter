from drf_yasg import openapi

import winter
from winter.routing import get_route
from winter.schema import QueryParametersInspector


class ControllerForQueryParameter:

    @winter.route_get()
    @winter.query_parameter('valid_query_param')
    @winter.query_parameter('mapped_query_param', map_to='invalid_query_param')
    def simple_method(
            self,
            valid_query_param: int,
            invalid_query_param: object,
    ):
        pass


def test_query_parameter_inspector():
    inspector = QueryParametersInspector()
    route = get_route(ControllerForQueryParameter.simple_method)
    # Act
    parameters = inspector.inspect_parameters(route)

    # Assert
    assert len(parameters) == 2
    parameter_by_name = {parameter.name: parameter for parameter in parameters}
    valid_parameter = parameter_by_name['valid_query_param']
    assert valid_parameter.type == openapi.TYPE_INTEGER
    assert valid_parameter.description == ''

    invalid_parameter = parameter_by_name['mapped_query_param']
    assert invalid_parameter.type == openapi.TYPE_STRING
    assert invalid_parameter.description == '(Note: parameter type can be wrong)'
