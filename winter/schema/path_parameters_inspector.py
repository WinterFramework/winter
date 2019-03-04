import typing
from typing import List

from drf_yasg import openapi

from .generation import get_argument_type_info
from .method_arguments_inspector import MethodArgumentsInspector
from .type_inspection import TypeInfo
from .utils import update_doc_with_invalid_hype_hint
from ..core import ComponentMethodArgument
from ..routing import Route

if typing.TYPE_CHECKING:  # pragma: no cover
    from ..routing import Route


class PathParametersInspector(MethodArgumentsInspector):
    _default_type_info = TypeInfo(openapi.TYPE_STRING)

    def inspect_parameters(self, route: 'Route') -> List[openapi.Parameter]:
        parameters = []

        for argument in self._path_arguments(route):
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

    def _path_arguments(self, route: Route) -> typing.List[ComponentMethodArgument]:
        path_arguments = []
        for path_variable in route.path_variables:
            argument = route.method.get_argument(path_variable)
            if argument is not None:
                path_arguments.append(argument)
        return path_arguments
