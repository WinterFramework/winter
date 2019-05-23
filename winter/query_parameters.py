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


@dataclasses.dataclass
class QueryParameterAnnotation:
    name: str
    map_to: str = None
    explode: bool = False

    def __post_init__(self):
        if self.map_to is None:
            self.map_to = self.name

    def __eq__(self, other):
        return isinstance(other, QueryParameterAnnotation) and (self.name == other.name or self.map_to == other.map_to)


def map_query_parameter(name: str, *, to: str):
    annotation = QueryParameterAnnotation(name, to)

    def wrapper(func_or_method):
        if not isinstance(func_or_method, ComponentMethod):
            return annotate_method(annotation)(func_or_method)
        annotations = func_or_method.annotations.get(QueryParameterAnnotation)
        for existing_annotation in annotations:
            if existing_annotation.map_to == to:
                raise ValueError()

        for existing_annotation in annotations:
            if existing_annotation.name == annotation.name:
                existing_annotation.map_to = to
                return func_or_method
        return annotate_method(annotation)(func_or_method)

    return wrapper


def get_query_param_annotation(method: ComponentMethod, mapped_to: str) -> Optional[QueryParameterAnnotation]:
    for query_param_annotation in method.annotations.get(QueryParameterAnnotation):
        if query_param_annotation.map_to == mapped_to:
            return query_param_annotation
    return None


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

        query_param_annotation = get_query_param_annotation(argument.method, argument.name)
        if query_param_annotation is None:
            self._cache[argument] = None
            return None

        parameter_name, explode = query_param_annotation.name, query_param_annotation.explode

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
