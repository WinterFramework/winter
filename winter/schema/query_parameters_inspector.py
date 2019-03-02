import typing
from typing import List

from drf_yasg import openapi

from .generation import get_argument_type_info
from .method_arguments_inspector import MethodArgumentsInspector
from .type_inspection import TypeInfo
from .utils import update_doc_with_invalid_hype_hint

if typing.TYPE_CHECKING:  # pragma: no cover
    from ..routing import Route


class QueryParametersInspector(MethodArgumentsInspector):
    _default_type_info = TypeInfo(openapi.TYPE_STRING)

    def inspect_parameters(self, route: 'Route') -> List[openapi.Parameter]:
        parameters = []

        for argument, query_parameter_name in route.query_arguments:

            default = argument.default if argument.has_default() else None

            type_info = get_argument_type_info(argument)

            description = argument.description

            if type_info is None:
                type_info = self._default_type_info
                description = update_doc_with_invalid_hype_hint(description)

            parameter = openapi.Parameter(
                name=query_parameter_name,
                description=description,
                required=argument.required,
                in_=openapi.IN_QUERY,
                default=default,
                **type_info.as_dict(),
            )
            parameters.append(parameter)

        return parameters
