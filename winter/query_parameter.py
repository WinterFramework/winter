import inspect
from collections import defaultdict
from typing import Optional

import django.http
import pydantic
from pydantic.dataclasses import dataclass
from rest_framework.exceptions import ParseError

from . import type_utils
from .argument_resolver import ArgumentResolver
from .controller import ControllerMethodArgument

_query_parameter_mappings = defaultdict(dict)


def _register_query_parameter_mapping(function, query_parameter_name: str, map_to: str):
    _query_parameter_mappings[function][map_to] = query_parameter_name


def query_parameter(query_parameter_name: str, map_to: str = None):
    map_to = map_to or query_parameter_name

    def wrapper(func):
        _register_query_parameter_mapping(func, query_parameter_name, map_to)
        return func
    return wrapper


def get_query_param_mapping(func, name: str) -> Optional[str]:
    mapping = _query_parameter_mappings.get(func)
    if not mapping:
        return None
    return mapping.get(name)


class QueryParameterResolver(ArgumentResolver):
    def is_supported(self, argument: ControllerMethodArgument) -> bool:
        return get_query_param_mapping(argument.method.func, argument.name) is not None

    def resolve_argument(self, argument: ControllerMethodArgument, http_request: django.http.HttpRequest):
        query_parameters = http_request.GET
        query_parameter_name = get_query_param_mapping(argument.method.func, argument.name)
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

        @dataclass
        class FieldData:
            value: argument.type_

        try:
            return FieldData(query_parameter_value).value
        except pydantic.ValidationError:
            raise ParseError(f'Invalid query parameter "{query_parameter_name}" value "{query_parameter_value}"')
