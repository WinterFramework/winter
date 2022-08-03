from typing import List

from drf_yasg import openapi

from winter.core import ComponentMethodArgument
from winter.web.routing import Route
from .route_parameters_inspector import RouteParametersInspector
from .type_inspection import InspectorNotFound
from .type_inspection import TypeInfo
from .type_inspection import inspect_type


class PathParametersInspector(RouteParametersInspector):

    def inspect_parameters(self, route: 'Route') -> List[openapi.Parameter]:
        parameters = []

        for argument in self._path_arguments(route):
            openapi_parameter = self._convert_argument_to_openapi_parameter(argument)
            parameters.append(openapi_parameter)

        return parameters

    def _convert_argument_to_openapi_parameter(self, argument: ComponentMethodArgument) -> openapi.Parameter:
        try:
            type_info = inspect_type(argument.type_)
            description = argument.description
        except InspectorNotFound:
            type_info = TypeInfo(openapi.TYPE_STRING)
            description = 'winter_openapi has failed to inspect the parameter'
        return openapi.Parameter(
            name=argument.name,
            description=description,
            required=True,
            in_=openapi.IN_PATH,
            default=argument.get_default(None),
            **type_info.as_dict(output=False),
        )

    def _path_arguments(self, route: 'Route') -> List[ComponentMethodArgument]:
        path_arguments = []
        for path_variable in route.get_path_variables():
            argument = route.method.get_argument(path_variable)
            if argument is not None:
                path_arguments.append(argument)
        return path_arguments
