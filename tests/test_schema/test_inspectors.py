from drf_yasg import openapi

import winter
from winter.schema import PathParametersInspector
from winter.schema import QueryParametersInspector


@winter.route('testing-inspectors/')
class ControllerForTestingInspectors:

    @winter.route('{valid_param}/{invalid_param}/{not_in_method}/')
    @winter.query_parameter('valid_query_param')
    @winter.query_parameter('mapped_query_param', map_to='invalid_query_param')
    def simple_method(
            self,
            valid_param: int,
            invalid_param: object,
            valid_query_param: int,
            invalid_query_param: object
    ):
        """
        :param valid_param: Valid doc
        :param invalid_param: Invalid doc
        """
        pass


def test_path_parameter_inspector():
    inspector = PathParametersInspector()

    # Act
    parameters = inspector.inspect_parameters(ControllerForTestingInspectors.simple_method)

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


def test_query_parameter_inspector():
    inspector = QueryParametersInspector()

    # Act
    parameters = inspector.inspect_parameters(ControllerForTestingInspectors.simple_method)

    # Assert
    assert len(parameters) == 2
    parameter_by_name = {parameter.name: parameter for parameter in parameters}
    valid_parameter = parameter_by_name['valid_query_param']
    assert valid_parameter.type == openapi.TYPE_INTEGER
    assert valid_parameter.description == ''

    invalid_parameter = parameter_by_name['mapped_query_param']
    assert invalid_parameter.type == openapi.TYPE_STRING
    assert invalid_parameter.description == '(Note: parameter type can be wrong)'
