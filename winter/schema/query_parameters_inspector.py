from typing import List

from drf_yasg import openapi

from .generation import get_argument_type_info
from .method_arguments_inspector import MethodArgumentsInspector
from .utils import update_doc_with_invalid_hype_hint
from ..core import ComponentMethod
from ..query_parameter import get_query_param_mapping


class QueryParametersInspector(MethodArgumentsInspector):

    def inspect_parameters(self, method: ComponentMethod) -> List[openapi.Parameter]:
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
                description = update_doc_with_invalid_hype_hint(argument.description)

            else:
                type_info_data = type_info.as_dict()
                description = argument.description

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
