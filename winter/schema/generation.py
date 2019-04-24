import typing
from typing import List

import docstring_parser
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .method_arguments_inspector import get_method_arguments_inspectors
from .type_inspection import InspectorNotFound
from .type_inspection import inspect_type
from .utils import update_doc_with_invalid_hype_hint
from ..core import ComponentMethod
from ..core import ComponentMethodArgument
from ..drf import get_input_serializer
from ..drf import get_output_serializer
from ..exceptions.handlers import MethodExceptionsHandler
from ..exceptions.handlers import exceptions_handler
from ..response_status import get_default_response_status
from ..routing import Route
from ..schema.type_inspection import TypeInfo


def generate_swagger_for_operation(view_func, controller_class, route: Route):
    method = route.method
    docstring = docstring_parser.parse(method.func.__doc__)
    input_serializer = get_input_serializer(method)
    if input_serializer:
        request_body = input_serializer.class_
    else:
        request_body = None
    manual_parameters = _build_method_parameters(route)
    responses = build_responses_schemas(route)
    swagger_auto_schema(
        operation_id=f'{controller_class.__name__}.{method.func.__name__}',
        operation_description=docstring.short_description,
        request_body=request_body,
        manual_parameters=manual_parameters,
        responses=responses,
    )(view_func)


def build_responses_schemas(route: Route):
    responses = {}
    http_method = route.http_method
    response_status = str(get_default_response_status(http_method, route.method))

    responses[response_status] = build_response_schema(route.method)
    method_exceptions_handler = MethodExceptionsHandler(route.method)

    for exception_cls in method_exceptions_handler.exception_classes:
        handler = method_exceptions_handler.get_handler(exception_cls)
        if handler is None:
            handler = exceptions_handler.get_handler(exception_cls)
        if handler is None:
            continue
        response_status = str(get_default_response_status(http_method, handler.handle_method))
        responses[response_status] = build_response_schema(handler.handle_method)
    return responses


def build_response_schema(method: ComponentMethod):
    output_serializer = get_output_serializer(method)
    if output_serializer is not None:
        return output_serializer.class_(**output_serializer.kwargs)

    type_hints = typing.get_type_hints(method.func)
    return_value_type = type_hints.get('return', None)
    try:
        type_info = inspect_type(return_value_type)
    except InspectorNotFound:
        return openapi.Response(description='')
    else:
        return type_info.get_openapi_schema()


def _build_method_parameters(route: Route) -> List[openapi.Parameter]:
    parameters = []
    for method_inspector in get_method_arguments_inspectors():
        parameters += method_inspector.inspect_parameters(route)
    return parameters


def get_argument_info(argument: ComponentMethodArgument) -> dict:
    try:
        type_info = inspect_type(argument.type_)
        invalid_hype_hint = False
    except InspectorNotFound:
        type_info = TypeInfo(openapi.TYPE_STRING)
        invalid_hype_hint = True
    type_info_data = type_info.as_dict()

    description = argument.description

    if invalid_hype_hint:
        description = update_doc_with_invalid_hype_hint(description)
    default = argument.get_default(None)
    type_info_data['description'] = description
    type_info_data['default'] = default
    return type_info_data
