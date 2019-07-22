import inspect
import typing
from typing import List

from django.http.response import HttpResponseBase
from drf_yasg import openapi

from .method_arguments_inspector import get_method_arguments_inspectors
from .type_inspection import InspectorNotFound
from .type_inspection import inspect_type
from .utils import update_doc_with_invalid_hype_hint
from .. import type_utils
from ..core import ComponentMethod
from ..core import ComponentMethodArgument
from ..drf import get_output_serializer
from ..exceptions.handlers import MethodExceptionsHandler
from ..exceptions.handlers import exceptions_handler
from ..response_entity import ResponseEntity
from ..response_status import get_default_response_status
from ..routing import Route
from ..schema.type_inspection import TypeInfo

_schema_titles: typing.Dict[str, typing.List] = {}


class CanNotInspectReturnType(Exception):

    def __init__(
        self,
        method: ComponentMethod,
        return_type: typing.Any,
        message: str,
    ):
        self._return_type = return_type
        self._message = message
        self._method = method

    def __repr__(self):
        return f'{self.__class__.__name__}({self})'

    def __str__(self):
        component_cls = self._method.component.component_cls
        method_path = f'{component_cls.__module__}.{self._method.full_name}'
        return f'{method_path}: -> {self._return_type}: {self._message}'


def get_schema_title(argument: ComponentMethodArgument) -> str:
    title = type_utils.get_type_name(argument.type_)
    dtos = _schema_titles.setdefault(title, [])

    if argument.type_ not in dtos:
        dtos.append(argument.type_)
    index = dtos.index(argument.type_)

    if not index:
        return title

    return title + f'{index}'


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

    return_value_type = method.return_value_type

    if (
        return_value_type in (None, type(None))
        or (inspect.isclass(return_value_type) and issubclass(return_value_type, (HttpResponseBase, ResponseEntity)))
    ):
        return openapi.Response(description='')

    try:
        type_info = inspect_type(return_value_type)
    except InspectorNotFound as e:
        raise CanNotInspectReturnType(method, return_value_type, str(e))
    return type_info.get_openapi_schema()


def build_method_parameters(route: Route) -> List['openapi.Parameter']:
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
