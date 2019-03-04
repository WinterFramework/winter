import typing
from typing import List

from drf_yasg import openapi

from .generation import get_argument_info
from .method_arguments_inspector import MethodArgumentsInspector
from ..core import ComponentMethodArgument
from ..query_parameter import QueryParameterAnnotation

if typing.TYPE_CHECKING:  # pragma: no cover
    from ..routing import Route


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

    def _query_arguments(self, route) -> typing.List[typing.Tuple[ComponentMethodArgument, str]]:
        query_arguments = []

        annotations = route.method.annotations.get(QueryParameterAnnotation)

        for query_parameter_annotation in annotations:
            argument = route.method.get_argument(query_parameter_annotation.map_to)
            if argument is not None:
                query_arguments.append((argument, query_parameter_annotation.name))
        return query_arguments
