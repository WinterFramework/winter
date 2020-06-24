from typing import List

from drf_yasg import openapi

from winter.core import ComponentMethodArgument
from winter.web.routing import Route
from .generation import get_argument_info
from .method_arguments_inspector import MethodArgumentsInspector


class PathParametersInspector(MethodArgumentsInspector):

    def inspect_parameters(self, route: 'Route') -> List[openapi.Parameter]:
        parameters = []

        for argument in self._path_arguments(route):
            parameter_data = get_argument_info(argument)
            parameter = openapi.Parameter(
                name=argument.name,
                required=True,
                in_=openapi.IN_PATH,
                **parameter_data,
            )
            parameters.append(parameter)

        return parameters

    def _path_arguments(self, route: 'Route') -> List[ComponentMethodArgument]:
        path_arguments = []
        for path_variable in route.get_path_variables():
            argument = route.method.get_argument(path_variable)
            if argument is not None:
                path_arguments.append(argument)
        return path_arguments
