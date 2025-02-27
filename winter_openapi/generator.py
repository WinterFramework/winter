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
from typing import Tuple
from typing import Type
from typing import Union

from django.http.response import HttpResponseBase
from openapi_pydantic import schema_validate
from openapi_pydantic.v3.v3_0 import Components
from openapi_pydantic.v3.v3_0 import Info
from openapi_pydantic.v3.v3_0 import MediaType as MediaTypeModel
from openapi_pydantic.v3.v3_0 import OpenAPI
from openapi_pydantic.v3.v3_0 import Operation
from openapi_pydantic.v3.v3_0 import Parameter
from openapi_pydantic.v3.v3_0 import PathItem
from openapi_pydantic.v3.v3_0 import Paths
from openapi_pydantic.v3.v3_0 import Reference
from openapi_pydantic.v3.v3_0 import RequestBody
from openapi_pydantic.v3.v3_0 import Response
from openapi_pydantic.v3.v3_0 import Responses
from openapi_pydantic.v3.v3_0 import Schema
from openapi_pydantic.v3.v3_0 import Server
from openapi_pydantic.v3.v3_0 import Tag

from winter.core import ComponentMethod
from winter.web import MediaType
from winter.web.default_response_status import get_response_status
from winter.web.exceptions import MethodExceptionsManager
from winter.web.request_body_annotation import RequestBodyAnnotation
from winter.web.routing import Route
from winter.web.routing import RouteAnnotation
from winter_openapi.inspection.inspection import inspect_type
from .inspection import DataTypes
from .inspection import TypeInfo
from .inspection.inspection import InspectorNotFound
from .inspectors import get_route_parameters_inspectors


class SchemaRegistry:
    def __init__(self):
        self._schemas: Dict[Tuple[Type, bool], Schema] = {}
        self._types_by_titles: Dict[str, Type] = {}

    def get_schema_or_reference(self, type_info: Union[Type, TypeInfo], output: bool) -> Union[Schema, Reference]:
        if not isinstance(type_info, TypeInfo):
            type_info = inspect_type(type_info)
        schema = self._schemas.get((type_info.hint_class, output))
        if not schema:
            schema = self.build_schema(type_info, output=output)
            if not schema.title:
                return schema
            if schema.nullable:
                schema.nullable = None
            self._schemas[type_info.hint_class, output] = schema

        if schema.title not in self._types_by_titles:
            self._types_by_titles[schema.title] = type_info.hint_class
        elif self._types_by_titles[schema.title] != type_info.hint_class:
            raise ValueError(f'Title {schema.title} for type {type_info.hint_class} is already used for another type: {self._types_by_titles[schema.title]}')

        reference = Reference(ref='#/components/schemas/' + schema.title)

        if type_info.nullable and schema.type == 'object':
            # https://stackoverflow.com/questions/40920441/how-to-specify-a-property-can-be-null-or-a-reference-with-swagger
            # Better solution, but not implemented yet https://github.com/OpenAPITools/openapi-generator/issues/9083
            return Schema(nullable=True, allOf=[reference])

        return reference

    def get_schemas(self) -> Dict[str, Schema]:
        return {
            schema.title: schema
            for schema in self._schemas.values()
        }

    def build_schema(self, type_info: TypeInfo, *, output: bool) -> Schema:
        if type_info.type_ == DataTypes.ANY:
            return Schema(
                description='Can be any value - string, number, boolean, array or object.',
                nullable=type_info.nullable,
            )

        data = {
            'type': type_info.type_,
        }

        if type_info.nullable:
            data['nullable'] = True

        if type_info.title:
            data['title'] = type_info.title if output else f'{type_info.title}Input'

        if type_info.description:
            data['description'] = type_info.description

        if type_info.format_ is not None:
            data['schema_format'] = type_info.format_

        if type_info.child is not None:
            data['items'] = self.get_schema_or_reference(type_info.child, output=output)

        if type_info.enum is not None:
            data['enum'] = type_info.enum

        if type_info.properties:
            sorted_keys = sorted(type_info.properties.keys())
            data['properties'] = {
                key: self.get_schema_or_reference(type_info.properties[key], output=output)
                for key in sorted_keys
            }

        if output:
            required_properties = list(type_info.properties)
        else:
            required_properties = [
                property_name
                for property_name in type_info.properties
                if property_name not in type_info.properties_defaults
                   and not type_info.properties[property_name].nullable
                   and not type_info.properties[property_name].can_be_undefined
            ]

        if required_properties:
            data['required'] = required_properties

        return Schema(**data)


def generate_openapi(
    title: str,
    version: str,
    routes: Sequence[Route],
    description: Optional[str] = None,
    tags: Optional[List[Dict[str, Any]]] = None,
    validate: bool = True,
    add_url_segment_as_tag: bool = True,
) -> Dict[str, Any]:
    routes = list(routes)
    routes.sort(key=lambda r: r.url_path)
    schema_registry = SchemaRegistry()
    tags_ = [Tag(**tag) for tag in tags or []]
    tag_names = [tag_.name for tag_ in tags_]
    paths: Paths = {}
    operation_ids: Set[str] = set()
    path_prefix = determine_path_prefix([route.url_path for route in routes])

    for url_path, group_routes in groupby(routes, key=lambda r: r.url_path):
        url_path_without_prefix = get_url_path_without_prefix(url_path, path_prefix)

        if not url_path_without_prefix.startswith('/'):
            url_path_without_prefix = '/' + url_path_without_prefix

        path_tag_names = list(tag_names)
        if add_url_segment_as_tag:
            url_path_tag = get_url_path_tag(url_path, path_prefix)
            if url_path_tag:
                path_tag_names.append(url_path_tag)

        path_item = _get_openapi_path(
            routes=group_routes,
            operation_ids=operation_ids,
            tag_names=path_tag_names,
            schema_registry=schema_registry,
        )
        paths[url_path_without_prefix] = path_item

    info = Info(title=title, version=version, description=description)
    servers_ = [Server(url=path_prefix)]
    components = Components(
        schemas=schema_registry.get_schemas(),
        responses={},
        parameters={},
    )
    openapi = OpenAPI(openapi="3.0.3", info=info, servers=servers_, paths=paths, components=components, tags=tags_)
    openapi_dict = openapi.dict(by_alias=True, exclude_none=True)
    if validate:
        schema_validate(openapi_dict)
    return openapi_dict


def _get_openapi_path(
    *,
    routes: Iterable[Route],
    operation_ids: Set[str],
    tag_names: Iterable[str],
    schema_registry: SchemaRegistry,
) -> PathItem:
    path = {}
    for route in routes:
        operation_id = route.method.full_name
        if operation_id in operation_ids:
            warnings.warn(f"Duplicate Operation ID {operation_id}")
        operation_ids.add(operation_id)

        try:
            operation = _get_openapi_operation(
                route=route,
                operation_id=operation_id,
                tag_names=tag_names,
                schema_registry=schema_registry,
            )
        except InspectorNotFound as e:
            raise CanNotInspectType(route.method, str(e))
        path[route.http_method.lower()] = operation

    return PathItem.parse_obj(path)


def _get_openapi_operation(
    *,
    route: Route,
    operation_id: str,
    tag_names: Iterable[str],
    schema_registry: SchemaRegistry,
) -> Operation:
    summary = route.method.docstring.short_description
    description = route.method.docstring.long_description
    operation_parameters = get_route_parameters(route, schema_registry)
    operation_request_body = get_request_body_parameters(route, schema_registry)
    operation_responses = get_responses_schemas(route, schema_registry)
    return Operation(
        tags=tag_names,
        summary=summary,
        description=description,
        operationId=operation_id,
        requestBody=operation_request_body,
        responses=operation_responses,
        parameters=operation_parameters,
    )


class CanNotInspectType(Exception):

    def __init__(
        self,
        method: ComponentMethod,
        message: str,
    ):
        self._message = message
        self._method = method

    def __repr__(self):
        return f'{self.__class__.__name__}({self})'

    def __str__(self):
        component_cls = self._method.component.component_cls
        method_path = f'{component_cls.__module__}.{self._method.full_name}'
        return f'{method_path}: {self._message}'


def get_url_path_without_prefix(url_path: str, path_prefix: str) -> str:
    # TODO: use removeprefix when python 3.9 will be used
    path_prefix_stripped = path_prefix.lstrip('/')
    url_path_stripped = url_path.lstrip('/')

    if path_prefix_stripped and url_path_stripped.startswith(path_prefix_stripped):
        return url_path_stripped[len(path_prefix_stripped):]
    else:
        return url_path


def get_url_path_tag(url_path: str, path_prefix: str) -> Optional[str]:
    path_prefix_segments = path_prefix.lstrip('/').split('/')
    url_path_segments = url_path.lstrip('/').split('/')
    path_prefix_segments = [segment for segment in path_prefix_segments if segment]  # remove empty segments like ['']

    # for the cases with single route
    if len(url_path_segments) <= len(path_prefix_segments):
        if len(url_path_segments) == len(path_prefix_segments):
            return None
        else:
            raise ValueError(f'Invalid path prefix {path_prefix} for url_path {url_path}')

    url_path_tag = url_path_segments[len(path_prefix_segments)]

    if url_path_tag.startswith('{'):
        return None

    return url_path_tag


def get_route_parameters(route: Route, schema_registry: SchemaRegistry) -> List[Parameter]:
    parameters = []
    for inspector in get_route_parameters_inspectors():
        parameters += inspector.inspect_parameters(route, schema_registry)
    return parameters


def get_request_body_parameters(route: Route, schema_registry: SchemaRegistry) -> Optional[RequestBody]:
    method = route.method
    request_body_annotation = method.annotations.get_one_or_none(RequestBodyAnnotation)
    if request_body_annotation is None:
        return None

    description = method.docstring.short_description
    argument = method.get_argument(request_body_annotation.argument_name)
    reference = schema_registry.get_schema_or_reference(argument.type_, output=False)

    route_annotation = method.annotations.get_one_or_none(RouteAnnotation)
    consumes = route_annotation.consumes or [MediaType.APPLICATION_JSON]
    content = {
        str(consume): MediaTypeModel(media_type_schema=reference)
        for consume in consumes
    }
    return RequestBody(description=description, content=content)


def get_responses_schemas(route: Route, schema_registry: SchemaRegistry) -> Responses:
    responses: Responses = {}
    http_method = route.http_method
    response_status = str(get_response_status(http_method, route.method))

    responses[response_status] = _build_response_schema(route.method, schema_registry)
    method_exceptions_manager = MethodExceptionsManager(route.method)

    for exception_cls in method_exceptions_manager.declared_exception_classes:
        handler = method_exceptions_manager.get_handler(exception_cls)
        handle_method = ComponentMethod.get_or_create(handler.__class__.handle)
        response_status = str(get_response_status(http_method, handle_method))
        responses[response_status] = _build_response_exception_handler_schema(handle_method, schema_registry)
    return responses


def determine_path_prefix(url_paths: List[str]) -> str:
    """
    https://github.com/encode/django-rest-framework/blob/master/LICENSE.md
    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
    WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
    USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

    Given a list of all paths, return the common prefix which should be
    discounted when generating a schema structure.

    This will be the longest common string that does not include that last
    component of the URL, or the last component before a path parameter.

    For example:

    /api/v1/users/
    /api/v1/users/{pk}/

    The path prefix is '/api/v1'
    """
    prefixes = []
    for path in url_paths:
        components = path.strip('/').split('/')
        initial_components = []
        for component in components:
            if '{' in component:
                break
            initial_components.append(component)
        prefix = '/'.join(initial_components[:-1])
        if not prefix:
            # We can just break early in the case that there's at least
            # one URL that doesn't have a path prefix.
            return '/'
        prefixes.append('/' + prefix + '/')

    split_paths = [path.strip('/').split('/') for path in prefixes]
    s1 = min(split_paths)
    s2 = max(split_paths)
    common = s1

    for i, c in enumerate(s1):
        if c != s2[i]:
            common = s1[:i]
            break

    return '/' + '/'.join(common)


def _build_response_schema(method: ComponentMethod, schema_registry: SchemaRegistry) -> Response:
    return_value_type = method.return_value_type
    if _is_abstract_or_none_return_type(return_value_type):
        return Response(description='')

    reference = schema_registry.get_schema_or_reference(return_value_type, output=True)
    route_annotation = method.annotations.get_one_or_none(RouteAnnotation)
    produces = route_annotation.produces or [MediaType.APPLICATION_JSON]
    content = {
        str(produce): MediaTypeModel(media_type_schema=reference)
        for produce in produces
    }
    return Response(description='', content=content)


def _build_response_exception_handler_schema(method: ComponentMethod, schema_registry: SchemaRegistry) -> Response:
    return_value_type = method.return_value_type
    if _is_abstract_or_none_return_type(return_value_type):
        return Response(description='')

    reference = schema_registry.get_schema_or_reference(return_value_type, output=True)
    content = {str(MediaType.APPLICATION_JSON): MediaTypeModel(media_type_schema=reference)}
    return Response(description='', content=content)


def _is_abstract_or_none_return_type(return_value_type):
    return (
        return_value_type in (None, type(None)) or
        (
            inspect.isclass(return_value_type) and
            issubclass(return_value_type, HttpResponseBase)
        )
    )