from typing import List
from typing import Tuple

from drf_yasg import openapi

from winter.core import ComponentMethodArgument
from winter.web.routing import Route
from .generation import get_argument_info
from .method_arguments_inspector import MethodArgumentsInspector


class QueryParametersInspector(MethodArgumentsInspector):

    def inspect_parameters(self, route: 'Route') -> List[openapi.Parameter]:
        parameters = []

        for argument, query_parameter_name in self._query_arguments(route):

            parameter_data = get_argument_info(argument)

            parameter = openapi.Parameter(
                name=query_parameter_name,
                required=argument.required,
                in_=openapi.IN_QUERY,
                **parameter_data,
            )
            parameters.append(parameter)

        return parameters

    def _query_arguments(self, route: 'Route') -> List[Tuple[ComponentMethodArgument, str]]:
        query_arguments = []
        query_parameters = route.get_query_parameters()

        for query_parameter in query_parameters:
            argument = route.method.get_argument(query_parameter.map_to)
            if argument is not None:
                query_arguments.append((argument, query_parameter.name))
        return query_arguments
