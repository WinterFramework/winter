import inspect
from typing import Optional

import dataclasses
import django.http
import pydantic
from rest_framework.exceptions import ParseError

from . import type_utils
from .argument_resolver import ArgumentResolver
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

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return get_query_param_mapping(argument.method, argument.name) is not None

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: django.http.HttpRequest):
        query_parameters = http_request.GET
        query_parameter_name = get_query_param_mapping(argument.method, argument.name)
        if query_parameter_name not in query_parameters:
            default = argument.parameter.default
            if default is not inspect.Parameter.empty:
                return default
            elif type_utils.is_optional(argument.type_):
                return None
            else:
                raise ParseError(f'Missing required query parameter "{query_parameter_name}"')
        if type_utils.is_iterable(argument.type_):
            query_parameter_value = query_parameters.getlist(query_parameter_name)
        else:
            query_parameter_value = query_parameters[query_parameter_name]

        @pydantic.dataclasses.dataclass
        class FieldData:
            value: argument.type_

        try:
            return FieldData(query_parameter_value).value
        except pydantic.ValidationError:
            raise ParseError(f'Invalid query parameter "{query_parameter_name}" value "{query_parameter_value}"')
