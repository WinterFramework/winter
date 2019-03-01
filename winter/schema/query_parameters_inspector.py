from typing import List

from drf_yasg import openapi

from .docstring_parser import DocstringParser
from .generation import get_argument_type_info
from .method_arguments_inspector import MethodArgumentsInspector
from ..core import ComponentMethod
from ..query_parameter import get_query_param_mapping


class QueryParametersInspector(MethodArgumentsInspector):

    def inspect_parameters(self, method: ComponentMethod) -> List[openapi.Parameter]:
        docstring_parser = DocstringParser(method.func.__doc__)
        parameters = []

        for argument in method.arguments:
            query_parameter_name = get_query_param_mapping(argument.method, argument.name)

            if query_parameter_name is None:
                continue

            default_params = {}

            if argument.has_default():
                default_params['default'] = argument.default

            type_info = get_argument_type_info(argument)

            if type_info is None:
                type_info_data = {
                    'type': openapi.TYPE_STRING
                }
                invalid_type_hint = True
            else:
                type_info_data = type_info.as_dict()
                invalid_type_hint = False

            description = docstring_parser.get_description(query_parameter_name, invalid_type_hint)

            parameter = openapi.Parameter(
                name=query_parameter_name,
                description=description,
                required=argument.required,
                in_=openapi.IN_QUERY,
                **type_info_data,
                **default_params,
            )
            parameters.append(parameter)

        return parameters
