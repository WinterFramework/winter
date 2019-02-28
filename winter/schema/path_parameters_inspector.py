from typing import List

import docstring_parser
from drf_yasg import openapi

from .generation import get_argument_type_info
from .method_arguments_inspector import MethodArgumentsInspector
from .utils import update_doc_with_invalid_hype_hint
from ..core import ComponentMethod
from ..routing import get_route


class PathParametersInspector(MethodArgumentsInspector):

    def inspect_parameters(self, method: ComponentMethod) -> List[openapi.Parameter]:
        docstring = docstring_parser.parse(method.func.__doc__)
        params_docs = {param_doc.arg_name: param_doc for param_doc in docstring.params}
        route = get_route(method)
        parameters = []

        for path_variable_name in route.path_variables:
            argument = method.get_argument(path_variable_name)
            if argument is None:
                continue
            param_doc = params_docs.get(path_variable_name)
            description = param_doc.description if param_doc else ''
            type_info = get_argument_type_info(argument)

            if type_info is None:
                type_info_data = {'type': openapi.TYPE_STRING}
                description = update_doc_with_invalid_hype_hint(description)
            else:
                type_info_data = type_info.as_dict()

            parameter = openapi.Parameter(
                name=argument.name,
                description=description,
                required=True,
                in_=openapi.IN_PATH,
                **type_info_data,
            )
            parameters.append(parameter)

        return parameters
