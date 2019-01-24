import inspect
from typing import List

import docstring_parser
from drf_yasg import openapi

from .controller_method_inspector import ControllerMethodInspector
from .generation import _get_argument_type_info
from .. import type_utils
from ..controller import ControllerMethod
from ..query_parameter import get_query_param_mapping


class QueryParametersInspector(ControllerMethodInspector):
    def inspect_parameters(self, controller_method: ControllerMethod) -> List[openapi.Parameter]:
        docstring = docstring_parser.parse(controller_method.func.__doc__)
        params_docs = {param_doc.arg_name: param_doc for param_doc in docstring.params}

        parameters = []

        for argument in controller_method.arguments:
            query_parameter_name = get_query_param_mapping(argument.method.func, argument.name)
            if not query_parameter_name:
                continue
            param_doc = params_docs.get(query_parameter_name)
            description = param_doc.description if param_doc else ''
            default_params = {}
            default = argument.parameter.default
            if default is not inspect.Parameter.empty:
                default_params['default'] = default
            required = default is inspect.Parameter.empty and not type_utils.is_optional(argument.type_)
            type_info = _get_argument_type_info(argument)
            if not type_info:
                type_info = {'type': openapi.TYPE_STRING}
                description += ' (Note: parameter type can be wrong)'
            parameter = openapi.Parameter(
                name=query_parameter_name,
                description=description,
                required=required,
                in_=openapi.IN_QUERY,
                **type_info,
                **default_params,
            )
            parameters.append(parameter)

        return parameters
