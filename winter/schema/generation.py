from enum import Enum
from typing import List

import docstring_parser
from drf_yasg import openapi
# TODO: Uncomment this import once the new drf-yasg is released
# from drf_yasg.inspectors.field import get_basic_type_info_from_hint
from drf_yasg.utils import swagger_auto_schema

from .controller_method_inspector import get_controller_method_inspectors
from .type_hinting_patch import get_basic_type_info_from_hint
from ..controller import ControllerMethod
from ..controller import ControllerMethodArgument
from ..drf import get_input_serializer
from ..drf import get_output_serializer
from ..response_status import get_default_response_status
from ..type_utils import is_origin_type_subclasses


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
    if output_serializer:
        responses[response_status] = output_serializer.class_(**output_serializer.args)
    else:
        responses[response_status] = openapi.Response(description='Success')
    # TODO support response dataclasses, preferably implement in dataclasses.py to keep extensibility
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


def _get_argument_type_info(argument: ControllerMethodArgument) -> dict:
    if is_origin_type_subclasses(argument.type_, Enum):
        return _get_type_info_for_enum(argument.type_)
    type_info = get_basic_type_info_from_hint(argument.type_)
    if not type_info:
        type_info = {'type': openapi.TYPE_STRING}
    return type_info


def _get_type_info_for_enum(enum_class: Enum) -> dict:
    choices = [entry.value for entry in enum_class]
    return {
        'type': openapi.TYPE_STRING,
        'enum': choices,
    }
