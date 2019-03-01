from typing import List

from drf_yasg import openapi

from .generation import get_argument_type_info
from .method_arguments_inspector import MethodArgumentsInspector
from .utils import DocstringParser
from ..core import ComponentMethod
from ..routing import get_route


class PathParametersInspector(MethodArgumentsInspector):

    def inspect_parameters(self, method: ComponentMethod) -> List[openapi.Parameter]:
        docstring_parser = DocstringParser(method.func.__doc__)
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
                invalid_type_hint = True
            else:
                invalid_type_hint = False
                type_info_data = type_info.as_dict()

            parameter = openapi.Parameter(
                name=argument.name,
                description=docstring_parser.get_description(path_variable_name, invalid_type_hint),
                required=True,
                in_=openapi.IN_PATH,
                **type_info_data,
            )
            parameters.append(parameter)

        return parameters
