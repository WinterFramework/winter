import typing
from typing import Optional
from typing import Tuple

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
    explode: bool = False


@dataclasses.dataclass(frozen=True)
class MapQueryParameterAnnotation:
    name: str
    map_to: str


def map_query_parameter(name: str, *, to: str):
    annotation = MapQueryParameterAnnotation(name, to)
    return annotate_method(annotation)


def get_query_param(method: ComponentMethod, mapped_to: str) -> Tuple[Optional[str], Optional[bool]]:
    map_query_param_annotations = method.annotations.get(MapQueryParameterAnnotation)
    for map_query_param_annotation in map_query_param_annotations:
        if map_query_param_annotation.map_to == mapped_to:
            name = map_query_param_annotation.name
            query_param_annotations = method.annotations.get(QueryParameterAnnotation)
            for query_param_annotation in query_param_annotations:
                if query_param_annotation.name == name:
                    return name, query_param_annotation.explode
            raise ValueError(f'Query parameter is mapped but not registered: {name}')
    return None, None


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

        parameter_name, explode = get_query_param(argument.method, argument.name)
        if parameter_name is None:
            self._cache[argument] = None
            return None

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
