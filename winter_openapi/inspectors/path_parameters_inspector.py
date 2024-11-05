from typing import List
from typing import TYPE_CHECKING

from openapi_pydantic.v3.v3_0 import Parameter

from winter.core import ComponentMethodArgument
from winter.web.routing import Route
from .route_parameters_inspector import RouteParametersInspector

if TYPE_CHECKING:
    from winter_openapi.generator import SchemaRegistry


class PathParametersInspector(RouteParametersInspector):

    def inspect_parameters(self, route: 'Route', schema_registry: 'SchemaRegistry') -> List[Parameter]:
        parameters = []

        for argument in self._path_arguments(route):
            openapi_parameter = self._convert_argument_to_openapi_parameter(argument, schema_registry)
            parameters.append(openapi_parameter)

        return parameters

    def _convert_argument_to_openapi_parameter(
        self,
        argument: ComponentMethodArgument,
        schema_registry: 'SchemaRegistry',
    ) -> Parameter:
        schema = schema_registry.get_schema_or_reference(argument.type_, output=False)
        return Parameter(
            name=argument.name,
            description=argument.description,
            required=argument.required,
            param_in='path',
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
