from typing import List

from drf_yasg import openapi

from .generation import get_argument_type_info
from .method_arguments_inspector import MethodArgumentsInspector
from .utils import update_doc_with_invalid_hype_hint
from ..core import ComponentMethod
from ..routing import get_route


class PathParametersInspector(MethodArgumentsInspector):

    def inspect_parameters(self, method: ComponentMethod) -> List[openapi.Parameter]:
        route = get_route(method)
        parameters = []

        for path_variable_name in route.path_variables:
            argument = method.get_argument(path_variable_name)
            if argument is None:
                continue

            type_info = get_argument_type_info(argument)

            if type_info is None:
                type_info_data = {
                    'type': openapi.TYPE_STRING
                }
                description = update_doc_with_invalid_hype_hint(argument.description)
            else:
                type_info_data = type_info.as_dict()
                description = argument.description
            parameter = openapi.Parameter(
                name=argument.name,
                description=description,
                required=True,
                in_=openapi.IN_PATH,
                **type_info_data,
            )
            parameters.append(parameter)

        return parameters
