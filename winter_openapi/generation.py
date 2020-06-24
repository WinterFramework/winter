import inspect
from typing import Any
from typing import Dict
from typing import List

from django.http.response import HttpResponseBase
from drf_yasg import openapi

from winter.core import ComponentMethod
from winter.core import ComponentMethodArgument
from winter.core.utils.typing import get_type_name
from winter.web.default_response_status import get_default_response_status
from winter.web.exceptions import MethodExceptionsManager
from winter.web.exceptions import exception_handlers_registry
from winter.web.routing import Route
from winter_django import get_output_serializer
from .method_arguments_inspector import get_method_arguments_inspectors
from .type_inspection import InspectorNotFound
from .type_inspection import TypeInfo
from .type_inspection import inspect_type
from .utils import update_doc_with_invalid_hype_hint

_schema_titles: Dict[str, List] = {}


class CanNotInspectReturnType(Exception):

    def __init__(
        self,
        method: ComponentMethod,
        return_type: Any,
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
    title = get_type_name(argument.type_)
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
    method_exceptions_manager = MethodExceptionsManager(route.method)

    for exception_cls in method_exceptions_manager.declared_exception_classes:
        handler = method_exceptions_manager.get_handler(exception_cls)
        if handler is None:
            handler = exception_handlers_registry.get_handler(exception_cls)
        if handler is None:
            continue
        handle_method = ComponentMethod.get_or_create(handler.__class__.handle)
        response_status = str(get_default_response_status(http_method, handle_method))
        responses[response_status] = build_response_schema(handle_method)
    return responses


def build_response_schema(method: ComponentMethod):
    output_serializer = get_output_serializer(method)
    if output_serializer is not None:
        return output_serializer.class_(**output_serializer.kwargs)

    return_value_type = method.return_value_type

    if (
        return_value_type in (None, type(None))
        or (inspect.isclass(return_value_type) and issubclass(return_value_type, HttpResponseBase))
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
