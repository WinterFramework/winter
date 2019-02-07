from typing import List

import docstring_parser
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .controller_method_inspector import get_controller_method_inspectors
from .type_inspection import InspectorNotFound
from .type_inspection import inspect_type
from ..controller import ControllerMethod
from ..controller import ControllerMethodArgument
from ..drf import get_input_serializer
from ..drf import get_output_serializer
from ..response_status import get_default_response_status


def generate_swagger_for_operation(view_func, controller, controller_method: ControllerMethod):
    docstring = docstring_parser.parse(controller_method.func.__doc__)
    input_serializer = get_input_serializer(controller_method.func)
    if input_serializer:
        request_body = input_serializer.class_
    else:
        request_body = None
    manual_parameters = _build_method_parameters(controller_method)
    output_serializer = get_output_serializer(controller_method.func)
    response_status = get_default_response_status(controller_method)
    responses = {}
    if output_serializer is not None:
        responses[response_status] = output_serializer.class_(**output_serializer.kwargs)
    else:
        try:
            type_info = inspect_type(controller_method.return_value_type)
        except InspectorNotFound:
            responses[response_status] = openapi.Response(description='Success')
        else:
            responses[response_status] = type_info.get_openapi_schema()
    swagger_auto_schema(
        operation_id=f'{controller.__class__.__name__}.{controller_method.func.__name__}',
        operation_description=docstring.short_description,
        request_body=request_body,
        manual_parameters=manual_parameters,
        responses=responses,
    )(view_func)


def _build_method_parameters(controller_method: ControllerMethod) -> List[openapi.Parameter]:
    parameters = []
    for method_inspector in get_controller_method_inspectors():
        parameters += method_inspector.inspect_parameters(controller_method)
    return parameters


def get_argument_type_info(argument: ControllerMethodArgument) -> dict:
    try:
        type_info = inspect_type(argument.type_)
    except InspectorNotFound:
        return {'type': openapi.TYPE_STRING}
    else:
        return type_info.as_dict()

