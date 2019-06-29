import typing

import pydantic
from rest_framework.exceptions import ParseError
from rest_framework.request import Request

from winter import type_utils
from winter.core import ArgumentDoesNotHaveDefault
from ..routing import get_route
from ...argument_resolver import ArgumentNotSupported
from ...argument_resolver import ArgumentResolver
from ...core import ComponentMethodArgument


class QueryParameterArgumentResolver(ArgumentResolver):

    def __init__(self):
        super().__init__()
        self._cache = {}

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return self._get_cached_data(argument) is not None

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):
        query_parameters = http_request.query_params

        cached_data = self._get_cached_data(argument)

        if cached_data is None:
            raise ArgumentNotSupported(argument)

        parameter_name, pydantic_data_class, is_iterable, explode = cached_data

        if parameter_name not in query_parameters:
            try:
                return argument.get_default()
            except ArgumentDoesNotHaveDefault:
                raise ParseError(f'Missing required query parameter "{parameter_name}"')

        value = self._get_value(query_parameters, parameter_name, is_iterable, explode)

        try:
            return pydantic_data_class(value).value
        except pydantic.ValidationError:
            raise ParseError(f'Invalid query parameter "{parameter_name}" value "{value}"')

    def _get_cached_data(self, argument: ComponentMethodArgument):

        if argument in self._cache:
            return self._cache[argument]

        route = get_route(argument.method)
        query_parameter = next((
            query_parameter
            for query_parameter in route.get_query_parameters()
            if query_parameter.map_to == argument.name),
            None,
        )
        if query_parameter is None:
            self._cache[argument] = None
            return None

        parameter_name, explode = query_parameter.name, query_parameter.explode

        pydantic_data_class = self._create_pydantic_class(argument.type_)
        is_iterable = type_utils.is_iterable(argument.type_)
        cached_data = self._cache[argument] = parameter_name, pydantic_data_class, is_iterable, explode
        return cached_data

    @staticmethod
    def _get_value(parameters, parameter_name, is_iterable, explode):
        if is_iterable:
            if explode:
                return parameters.getlist(parameter_name)
            return parameters[parameter_name].split(',')
        else:
            return parameters[parameter_name]

    @staticmethod
    def _create_pydantic_class(type_) -> typing.Type:
        @pydantic.dataclasses.dataclass
        class PydanticDataclass:
            value: type_

        return PydanticDataclass
