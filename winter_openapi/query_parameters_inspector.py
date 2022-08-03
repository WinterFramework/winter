from typing import List
from typing import Tuple

from drf_yasg import openapi

from winter.core import ComponentMethodArgument
from winter.web.routing import Route
from .route_parameters_inspector import RouteParametersInspector
from .type_inspection import InspectorNotFound
from .type_inspection import TypeInfo
from .type_inspection import inspect_type


class QueryParametersInspector(RouteParametersInspector):

    def inspect_parameters(self, route: 'Route') -> List[openapi.Parameter]:
        parameters = []

        for argument, query_parameter_name in self._query_arguments(route):
            openapi_parameter = self._convert_argument_to_openapi_parameter(argument, query_parameter_name)
            parameters.append(openapi_parameter)

        return parameters

    def _convert_argument_to_openapi_parameter(self, argument: ComponentMethodArgument, name: str) -> openapi.Parameter:
        try:
            type_info = inspect_type(argument.type_)
            description = argument.description
        except InspectorNotFound:
            type_info = TypeInfo(openapi.TYPE_STRING)
            description = 'winter_openapi has failed to inspect the parameter'

        return openapi.Parameter(
            name=name,
            description=description,
            required=argument.required,
            in_=openapi.IN_QUERY,
            default=argument.get_default(None),
            **type_info.as_dict(output=False),
        )

    def _query_arguments(self, route: 'Route') -> List[Tuple[ComponentMethodArgument, str]]:
        query_arguments = []
        query_parameters = route.get_query_parameters()

        for query_parameter in query_parameters:
            argument = route.method.get_argument(query_parameter.map_to)
            if argument is not None:
                query_arguments.append((argument, query_parameter.name))
        return query_arguments
