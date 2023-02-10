import inspect
import warnings
from itertools import groupby
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set

from django.http.response import HttpResponseBase
from openapi_schema_pydantic.v3.v3_0_3 import Components
from openapi_schema_pydantic.v3.v3_0_3 import Info
from openapi_schema_pydantic.v3.v3_0_3 import MediaType as MediaTypeModel
from openapi_schema_pydantic.v3.v3_0_3 import OpenAPI
from openapi_schema_pydantic.v3.v3_0_3 import Operation
from openapi_schema_pydantic.v3.v3_0_3 import Parameter
from openapi_schema_pydantic.v3.v3_0_3 import PathItem
from openapi_schema_pydantic.v3.v3_0_3 import Paths
from openapi_schema_pydantic.v3.v3_0_3 import RequestBody
from openapi_schema_pydantic.v3.v3_0_3 import Response
from openapi_schema_pydantic.v3.v3_0_3 import Responses
from openapi_schema_pydantic.v3.v3_0_3 import Server
from openapi_schema_pydantic.v3.v3_0_3 import Tag

from winter.core import ComponentMethod
from winter.web import MediaType
from winter.web.default_response_status import get_default_response_status
from winter.web.exceptions import MethodExceptionsManager
from winter.web.exceptions import exception_handlers_registry
from winter.web.request_body_annotation import RequestBodyAnnotation
from winter.web.routing import Route
from winter.web.routing import RouteAnnotation
from winter_openapi.inspection.inspection import InspectorNotFound
from winter_openapi.inspection.inspection import inspect_type
from .inspectors import get_route_parameters_inspectors
from .type_info_converter import convert_type_info_to_openapi_schema


def generate_openapi(
    title: str,
    version: str,
    routes: Sequence[Route],
    description: Optional[str] = None,
    tags: Optional[List[Dict[str, Any]]] = None,
    servers: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    components: Components = Components(responses=[], schemas=[], parameters=[])
    tags_ = [Tag(**tag) for tag in tags or []]
    tag_names = [tag_.name for tag_ in tags_]
    paths: Paths = {}
    operation_ids: Set[str] = set()
    for key, group_routes in groupby(routes, key=lambda r: r.url_path):
        path = _get_openapi_path(route=group_routes, operation_ids=operation_ids, tag_names=tag_names)
        paths[key] = path

    info = Info(title=title, version=version, description=description)
    servers_ = [Server(**server) for server in servers or []]
    open_api = OpenAPI(info=info, servers=servers_, paths=paths, components=components, tags=tags_)
    return open_api.dict(by_alias=True, exclude_none=True)


def _get_openapi_path(*, route: Iterable[Route], operation_ids: Set[str], tag_names: Iterable[str]) -> PathItem:
    path = {}
    for route_item in route:
        operation_id = route_item.method.full_name
        if operation_id in operation_ids:
            warnings.warn(f"Duplicate Operation ID {operation_id}")
        operation_ids.add(operation_id)

        operation = _get_openapi_operation(route=route_item, operation_id=operation_id, tag_names=tag_names)
        path[route_item.http_method.lower()] = operation

    return PathItem.parse_obj(path)


def _get_openapi_operation(*, route: Route, operation_id: str, tag_names: Iterable[str]) -> Operation:
    summary = route.method.docstring.short_description
    description = route.method.docstring.long_description
    operation_parameters = get_route_parameters(route)
    operation_request_body = get_request_body_parameters(route)
    operation_responses = get_responses_schemas(route)
    return Operation(
        tags=tag_names,
        summary=summary,
        description=description,
        operationId=operation_id,
        requestBody=operation_request_body,
        responses=operation_responses,
        parameters=operation_parameters,
    )


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


def get_route_parameters(route: Route) -> List[Parameter]:
    parameters = []
    for inspector in get_route_parameters_inspectors():
        parameters += inspector.inspect_parameters(route)
    return parameters


def get_request_body_parameters(route: Route) -> Optional[RequestBody]:
    method = route.method
    request_body_annotation = method.annotations.get_one_or_none(RequestBodyAnnotation)
    if request_body_annotation is None:
        return None

    description = method.docstring.short_description
    argument = method.get_argument(request_body_annotation.argument_name)
    type_info = inspect_type(argument.type_)
    media_type_schema = convert_type_info_to_openapi_schema(type_info, output=False)

    route_annotation = method.annotations.get_one_or_none(RouteAnnotation)
    consumes = route_annotation.consumes or [MediaType.APPLICATION_JSON]
    content = {
        str(consume): MediaTypeModel(media_type_schema=media_type_schema)
        for consume in consumes
    }
    return RequestBody(description=description, content=content)


def get_responses_schemas(route: Route) -> Responses:
    responses: Responses = {}
    http_method = route.http_method
    response_status = str(get_default_response_status(http_method, route.method))

    responses[response_status] = _build_response_schema(route.method)
    method_exceptions_manager = MethodExceptionsManager(route.method)

    for exception_cls in method_exceptions_manager.declared_exception_classes:
        handler = method_exceptions_manager.get_handler(exception_cls)
        if handler is None:
            handler = exception_handlers_registry.get_handler(exception_cls)
        if handler is None:
            continue
        handle_method = ComponentMethod.get_or_create(handler.__class__.handle)
        response_status = str(get_default_response_status(http_method, handle_method))
        responses[response_status] = _build_response_exception_handler_schema(handle_method)
    return responses


def _build_response_schema(method: ComponentMethod) -> Response:
    return_value_type = method.return_value_type
    if _is_abstract_or_none_return_type(return_value_type):
        return Response(description='')

    type_info = _get_inspect_type(method, return_value_type)
    media_type_schema = convert_type_info_to_openapi_schema(type_info, output=True)
    route_annotation = method.annotations.get_one_or_none(RouteAnnotation)
    produces = route_annotation.produces or [MediaType.APPLICATION_JSON]
    content = {
        str(produce): MediaTypeModel(media_type_schema=media_type_schema)
        for produce in produces
    }
    return Response(description='', content=content)


def _build_response_exception_handler_schema(method: ComponentMethod) -> Response:
    return_value_type = method.return_value_type
    if _is_abstract_or_none_return_type(return_value_type):
        return Response(description='')

    type_info = _get_inspect_type(method, return_value_type)
    media_type_schema = convert_type_info_to_openapi_schema(type_info, output=True)
    content = {str(MediaType.APPLICATION_JSON): MediaTypeModel(media_type_schema=media_type_schema)}
    return Response(description='', content=content)


def _get_inspect_type(method, return_value_type):
    try:
        type_info = inspect_type(return_value_type)
    except InspectorNotFound as e:
        raise CanNotInspectReturnType(method, return_value_type, str(e))
    return type_info


def _is_abstract_or_none_return_type(return_value_type):
    return (
        return_value_type in (None, type(None)) or
        (
            inspect.isclass(return_value_type) and
            issubclass(return_value_type, HttpResponseBase)
        )
    )