import typing

import dataclasses
import pydantic
import rest_framework.request
from rest_framework.exceptions import ParseError
from uritemplate import URITemplate

from . import type_utils
from .argument_resolver import ArgumentNotSupported
from .argument_resolver import ArgumentResolver
from .core import ArgumentDoesNotHaveDefault
from .core import ComponentMethod
from .core import ComponentMethodArgument
from .core.annotation_decorator import annotate_method
from .routing.routing import get_url_path


@dataclasses.dataclass
class MapQueryParameterAnnotation:
    name: str
    map_to: str = None

    def __eq__(self, other):
        return isinstance(other, MapQueryParameterAnnotation) and (
                self.name == other.name or self.map_to == other.map_to)


@dataclasses.dataclass
class QueryParameter:
    name: str
    map_to: str
    explode: bool


def map_query_parameter(name: str, *, to: str):
    annotation = MapQueryParameterAnnotation(name, to)
    return annotate_method(annotation, unique=True)


def get_query_parameters(method: ComponentMethod) -> typing.List[QueryParameter]:
    url_path = get_url_path(method)
    query_parameters = []
    map_query_parameters_annotations = method.annotations.get(MapQueryParameterAnnotation)
    map_to_by_names = {
        map_query_parameter.name: map_query_parameter.map_to
        for map_query_parameter in map_query_parameters_annotations
    }

    query_variables = (variable for variable in URITemplate(url_path).variables if variable.operator == '?')
    for variable in query_variables:
        for variable_name, variable_params in variable.variables:
            map_to = map_to_by_names.get(variable_name, variable_name)
            query_parameter = QueryParameter(
                name=variable_name,
                map_to=map_to,
                explode=variable_params['explode'],
            )
            query_parameters.append(query_parameter)
    return query_parameters


class QueryParameterArgumentResolver(ArgumentResolver):

    def __init__(self):
        super().__init__()
        self._cache = {}

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return self._get_cached_data(argument) is not None

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: rest_framework.request.Request):
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

        query_parameters = get_query_parameters(argument.method)
        query_parameter = next((
            query_parameter
            for query_parameter in query_parameters
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
