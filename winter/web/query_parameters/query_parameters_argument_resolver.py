from typing import MutableMapping
from typing import Optional

import django.http

from winter.core import ArgumentDoesNotHaveDefault
from winter.core import ComponentMethodArgument
from winter.core.json import JSONDecodeException
from winter.core.json import json_decode
from winter.core.utils.typing import is_iterable_type
from .query_parameter import QueryParameter
from ..argument_resolver import ArgumentNotSupported
from ..argument_resolver import ArgumentResolver
from ..exceptions import RequestDataDecodeException
from ..routing import get_route


class QueryParameterArgumentResolver(ArgumentResolver):

    def __init__(self):
        super().__init__()
        self._query_parameters = {}

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return self._get_query_parameter(argument) is not None

    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: django.http.HttpRequest,
        response_headers: MutableMapping[str, str],
    ):
        query_parameters = request.GET

        query_parameter = self._get_query_parameter(argument)

        if query_parameter is None:
            raise ArgumentNotSupported(argument)

        parameter_name = query_parameter.name
        explode = query_parameter.explode
        is_iterable = is_iterable_type(argument.type_)

        if parameter_name not in query_parameters:
            try:
                return argument.get_default()
            except ArgumentDoesNotHaveDefault:
                raise RequestDataDecodeException(f'Missing required query parameter "{parameter_name}"')

        value = self._get_value(query_parameters, parameter_name, is_iterable, explode)

        try:
            return json_decode(value, argument.type_)
        except JSONDecodeException as e:
            raise RequestDataDecodeException(e.errors)

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
