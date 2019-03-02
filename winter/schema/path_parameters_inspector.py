import typing
from typing import List

from drf_yasg import openapi

from .generation import get_argument_type_info
from .method_arguments_inspector import MethodArgumentsInspector
from .type_inspection import TypeInfo
from .utils import update_doc_with_invalid_hype_hint
from ..routing import Route

if typing.TYPE_CHECKING:  # pragma: no cover
    from ..routing import Route


class PathParametersInspector(MethodArgumentsInspector):
    _default_type_info = TypeInfo(openapi.TYPE_STRING)

    def inspect_parameters(self, route: 'Route') -> List[openapi.Parameter]:
        parameters = []

        for argument in route.path_arguments:
            type_info = get_argument_type_info(argument)
            description = argument.description

            if type_info is None:
                type_info = self._default_type_info
                description = update_doc_with_invalid_hype_hint(description)

            parameter = openapi.Parameter(
                name=argument.name,
                description=description,
                required=True,
                in_=openapi.IN_PATH,
                **type_info.as_dict(),
            )
            parameters.append(parameter)

        return parameters
