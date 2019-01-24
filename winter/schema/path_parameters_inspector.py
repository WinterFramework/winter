from typing import List

import docstring_parser
import uritemplate
from drf_yasg import openapi

from .controller_method_inspector import ControllerMethodInspector
from .generation import _get_argument_type_info
from ..controller import ControllerMethod


class PathParametersInspector(ControllerMethodInspector):
    def inspect_parameters(self, controller_method: ControllerMethod) -> List[openapi.Parameter]:
        docstring = docstring_parser.parse(controller_method.func.__doc__)
        params_docs = {param_doc.arg_name: param_doc for param_doc in docstring.params}

        parameters = []

        for path_variable_name in uritemplate.variables(controller_method.url_path):
            argument = controller_method.get_argument(path_variable_name)
            if not argument:
                continue
            param_doc = params_docs.get(path_variable_name)
            description = param_doc.description if param_doc else ''
            type_info = _get_argument_type_info(argument)
            if not type_info:
                type_info = {'type': openapi.TYPE_STRING}
                description += ' (Note: parameter type can be wrong)'
            parameter = openapi.Parameter(
                name=argument.name,
                description=description,
                required=True,
                in_=openapi.IN_PATH,
                **type_info,
            )
            parameters.append(parameter)

        return parameters
