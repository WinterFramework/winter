from typing import MutableMapping
from typing import Optional

from rest_framework.request import Request

from ..routing import get_route
from ... import converters
from ... import type_utils
from ...argument_resolver import ArgumentNotSupported
from ...argument_resolver import ArgumentResolver
from ...core import ArgumentDoesNotHaveDefault
from ...core import ComponentMethodArgument
from ...routing.query_parameters import QueryParameter


class QueryParameterArgumentResolver(ArgumentResolver):

    def __init__(self):
        super().__init__()
        self._query_parameters = {}

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return self._get_query_parameter(argument) is not None

    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: Request,
        response_headers: MutableMapping[str, str],
    ):
        query_parameters = request.query_params

        query_parameter = self._get_query_parameter(argument)

        if query_parameter is None:
            raise ArgumentNotSupported(argument)

        parameter_name = query_parameter.name
        explode = query_parameter.explode
        is_iterable = type_utils.is_iterable(argument.type_)

        if parameter_name not in query_parameters:
            try:
                return argument.get_default()
            except ArgumentDoesNotHaveDefault:
                raise converters.ConvertException(f'Missing required query parameter "{parameter_name}"')

        value = self._get_value(query_parameters, parameter_name, is_iterable, explode)
        return converters.convert(value, argument.type_)

    def _get_query_parameter(self, argument: ComponentMethodArgument) -> Optional[QueryParameter]:
        if argument in self._query_parameters:
            return self._query_parameters[argument]

        route = get_route(argument.method)
        if route is None:
            return None

        query_parameter = next(
            (
                query_parameter
                for query_parameter in route.get_query_parameters()
                if query_parameter.map_to == argument.name
            ),
            None,
        )
        self._query_parameters[argument] = query_parameter
        return query_parameter

    @staticmethod
    def _get_value(parameters, parameter_name, is_iterable, explode):
        if is_iterable:
            if explode:
                return parameters.getlist(parameter_name)
            return parameters[parameter_name].split(',')
        else:
            return parameters[parameter_name]
