import typing
from typing import List

import docstring_parser
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .controller_method_inspector import get_controller_method_inspectors
from .type_inspection import InspectorNotFound
from .type_inspection import inspect_type
from ..core import ComponentMethod
from ..core import ComponentMethodArgument
from ..drf import get_input_serializer
from ..drf import get_output_serializer
from ..exceptions import exceptions_handler
from ..exceptions import get_throws
from ..response_status import get_default_response_status
from ..routing import Route


def generate_swagger_for_operation(view_func, controller, route: Route):
    method = route.method
    docstring = docstring_parser.parse(method.func.__doc__)
    input_serializer = get_input_serializer(method)
    if input_serializer:
        request_body = input_serializer.class_
    else:
        request_body = None
    manual_parameters = _build_method_parameters(method)
    responses = build_responses_schemas(route)
    swagger_auto_schema(
        operation_id=f'{controller.__class__.__name__}.{method.func.__name__}',
        operation_description=docstring.short_description,
        request_body=request_body,
        manual_parameters=manual_parameters,
        responses=responses,
    )(view_func)


def build_responses_schemas(route: Route):
    responses = {}
    response_status = str(get_default_response_status(route))
    try:
        responses[response_status] = build_response_schema(route)
    except InspectorNotFound:
        responses[response_status] = openapi.Response(description='Success')
    for exception_cls in get_throws(route.method):
        handler = exceptions_handler.get_handler(exception_cls)
        if handler is None:
            continue
        response_status = str(get_default_response_status(handler.route))
        try:
            responses[response_status] = build_response_schema(handler.route)
        except InspectorNotFound:
            continue
    return responses


def build_response_schema(route):
    method = route.method
    output_serializer = get_output_serializer(method)
    if output_serializer is not None:
        return output_serializer.class_(**output_serializer.kwargs)

    type_hints = typing.get_type_hints(method.func)
    return_value_type = type_hints.get('return', None)
    type_info = inspect_type(return_value_type)
    return type_info.get_openapi_schema()


def _build_method_parameters(method: ComponentMethod) -> List[openapi.Parameter]:
    parameters = []
    for method_inspector in get_controller_method_inspectors():
        parameters += method_inspector.inspect_parameters(method)
    return parameters


def get_argument_type_info(argument: ComponentMethodArgument) -> typing.Optional[dict]:
    try:
        type_info = inspect_type(argument.type_)
    except InspectorNotFound:
        return None
    else:
        return type_info.as_dict()
