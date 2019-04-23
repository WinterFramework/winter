import typing
from typing import Optional

import dataclasses
import pydantic
import rest_framework.request
from rest_framework.exceptions import ParseError

from . import type_utils
from .argument_resolver import ArgumentNotSupported
from .argument_resolver import ArgumentResolver
from .core import ArgumentDoesNotHaveDefault
from .core import ComponentMethod
from .core import ComponentMethodArgument
from .core.annotation_decorator import annotate_method


@dataclasses.dataclass(frozen=True)
class QueryParameterAnnotation:
    name: str
    map_to: str


def query_parameter(name: str, map_to: str = None):
    map_to = map_to if map_to is not None else name
    annotation = QueryParameterAnnotation(name, map_to)
    return annotate_method(annotation)


def get_query_param_mapping(method: ComponentMethod, map_to: str) -> Optional[str]:
    annotations = method.annotations.get(QueryParameterAnnotation)
    for query_parameter_annotation in annotations:
        if query_parameter_annotation.map_to == map_to:
            return query_parameter_annotation.name
    return None


class QueryParameterResolver(ArgumentResolver):

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

        parameter_name, pydantic_data_class, is_iterable = cached_data

        if parameter_name not in query_parameters:
            try:
                return argument.get_default()
            except ArgumentDoesNotHaveDefault:
                raise ParseError(f'Missing required query parameter "{parameter_name}"')

        value = self._get_value(query_parameters, parameter_name, is_iterable)

        try:
            return pydantic_data_class(value).value
        except pydantic.ValidationError:
            raise ParseError(f'Invalid query parameter "{parameter_name}" value "{value}"')

    def _get_value(self, parameters, parameter_name, is_iterable):
        if is_iterable:
            return parameters.getlist(parameter_name)
        else:
            return parameters[parameter_name]

    def _get_cached_data(self, argument: ComponentMethodArgument):

        if argument in self._cache:
            return self._cache[argument]

        parameter_name = get_query_param_mapping(argument.method, argument.name)
        if parameter_name is None:
            self._cache[argument] = None
            return None

        pydantic_data_class = self._create_pydantic_class(argument.type_)
        is_iterable = type_utils.is_iterable(argument.type_)
        cached_data = self._cache[argument] = parameter_name, pydantic_data_class, is_iterable
        return cached_data

    def _create_pydantic_class(self, type_) -> typing.Type:
        @pydantic.dataclasses.dataclass
        class PydanticDataclass:
            value: type_

        return PydanticDataclass
