import dataclasses
from typing import MutableMapping


from .query_parameter_argument_resolver import QueryParameterArgumentResolver
from .query_parameters_annotation import QueryParametersAnnotation
from ..argument_resolver import ArgumentResolver
from ..exceptions import RequestDataDecodeException
from ..routing import get_route
from winter.web.request import Request
from winter.components import ComponentMethodArgument
from winter.json import JSONDecodeException
from winter.json import json_decode
from winter.typing import is_iterable_type
from winter.typing import is_optional


class QueryParametersArgumentResolver(ArgumentResolver):
    """
    Maps the query parameters to the fields of the dataclass, as each one is mapped to an argument: a missing
    parameter takes the default of its field.
    """

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        annotation = argument.method.annotations.get_one_or_none(QueryParametersAnnotation)
        if annotation is None:
            return False
        return annotation.argument.name == argument.name

    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: Request,
        response_headers: MutableMapping[str, str],
    ):
        kwargs = {}
        query_parameters = get_route(argument.method).get_query_parameters()
        query_parameters_map = {query_parameter.name: query_parameter for query_parameter in query_parameters}
        for field in dataclasses.fields(argument.type_):
            if field.name not in request.query_parameters:
                if _has_default(field):
                    continue  # The dataclass sets the default
                if not is_optional(field.type):
                    raise RequestDataDecodeException(f'Missing required query parameter "{field.name}"')
                kwargs[field.name] = None
                continue
            value = QueryParameterArgumentResolver.get_value(
                request.query_parameters,
                field.name,
                is_iterable_type(field.type),
                query_parameters_map[field.name].explode,
            )
            try:
                kwargs[field.name] = json_decode(value, field.type)
            except JSONDecodeException as e:
                raise RequestDataDecodeException(e.errors)
        return argument.type_(**kwargs)


def _has_default(field: dataclasses.Field) -> bool:
    return field.default is not dataclasses.MISSING or field.default_factory is not dataclasses.MISSING
