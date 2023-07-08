from typing import List

from openapi_schema_pydantic.v3.v3_0_3 import Parameter

from winter.core import ComponentMethodArgument
from winter.web.routing import Route
from winter_openapi.inspection.inspection import InspectorNotFound
from winter_openapi.inspection.inspection import inspect_type
from winter_openapi.type_info_converter import convert_type_info_to_openapi_schema
from .route_parameters_inspector import RouteParametersInspector
from ..inspection import DataTypes
from ..inspection import TypeInfo


class PathParametersInspector(RouteParametersInspector):

    def inspect_parameters(self, route: 'Route') -> List[Parameter]:
        parameters = []

        for argument in self._path_arguments(route):
            openapi_parameter = self._convert_argument_to_openapi_parameter(argument)
            parameters.append(openapi_parameter)

        return parameters

    def _convert_argument_to_openapi_parameter(self, argument: ComponentMethodArgument) -> Parameter:
        try:
            type_info = inspect_type(argument.type_)
            description = argument.description
        except InspectorNotFound:
            type_info = TypeInfo(DataTypes.STRING)
            description = 'winter_openapi has failed to inspect the parameter'

        schema = convert_type_info_to_openapi_schema(type_info, output=False)
        return Parameter(
            name=argument.name,
            description=description,
            required=argument.required,
            param_in='path',
            default=argument.get_default(None),
            param_schema=schema,
        )

    def _path_arguments(self, route: 'Route') -> List[ComponentMethodArgument]:
        path_arguments = []
        for path_variable in route.get_path_variables():
            argument = route.method.get_argument(path_variable)
            if argument is None:
                raise ValueError(f'Path variable "{path_variable}" not found in method {route.method.full_name}')
            path_arguments.append(argument)
        return path_arguments
