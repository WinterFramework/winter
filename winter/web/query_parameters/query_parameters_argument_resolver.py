import dataclasses
from typing import MutableMapping

import django.http

from .query_parameter_argument_resolver import QueryParameterArgumentResolver
from .query_parameters_annotation import QueryParametersAnnotation
from ..argument_resolver import ArgumentResolver
from ..routing import get_route
from ...core import ComponentMethodArgument
from ...core.json import json_decode
from ...core.utils.typing import is_iterable_type


class QueryParametersArgumentResolver(ArgumentResolver):

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        annotation = argument.method.annotations.get_one_or_none(QueryParametersAnnotation)
        if annotation is None:
            return False
        return annotation.argument.name == argument.name

    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: django.http.HttpRequest,
        response_headers: MutableMapping[str, str],
    ):
        kwargs = {}
        query_parameters = get_route(argument.method).get_query_parameters()
        query_parameters_map = {query_parameter.name: query_parameter for query_parameter in query_parameters}
        for field in dataclasses.fields(argument.type_):
            value = QueryParameterArgumentResolver.get_value(
                request.GET,
                field.name,
                is_iterable_type(field.type),
                query_parameters_map[field.name].explode,
            )
            kwargs[field.name] = json_decode(value, field.type)
        return argument.type_(**kwargs)
