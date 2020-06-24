from typing import List
from typing import Optional

from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema as SwaggerAutoSchemaBase
from drf_yasg.utils import merge_params

from winter.web.request_body_annotation import RequestBodyAnnotation
from winter.web.routing import Route
from winter.web.routing import RouteAnnotation
from winter_django import InputSerializer
from .generation import build_method_parameters
from .generation import build_responses_schemas
from .generation import get_schema_title
from .type_inspection import inspect_type


class SwaggerAutoSchema(SwaggerAutoSchemaBase):

    def get_operation(self, operation_keys):
        route = self._get_route()
        if route is None:
            return super().get_operation(operation_keys)
        method = route.method
        consumes = self._get_consumes(route)
        produces = self._get_produces(route)

        body = self._get_request_body_parameters(route)
        manual_parameters = build_method_parameters(route)
        parameters = merge_params(body, manual_parameters)

        operation_id = method.full_name
        description = method.docstring.short_description
        deprecated = self.is_deprecated()
        responses = self._get_responses(route)
        tags = self.get_tags(operation_keys)

        return openapi.Operation(
            operation_id=operation_id,
            description=description,
            responses=responses,
            parameters=parameters,
            consumes=consumes,
            produces=produces,
            deprecated=deprecated,
            tags=tags,
        )

    def _get_responses(self, route: Route):
        responses_schemas = build_responses_schemas(route)
        return openapi.Responses(responses=self.get_response_schemas(responses_schemas))

    def _get_consumes(self, route: Route):
        route_annotation = route.method.annotations.get_one_or_none(RouteAnnotation)
        if route_annotation is None or route_annotation.consumes is None:
            return self.get_consumes()
        return [str(media_type) for media_type in route_annotation.consumes]

    def _get_produces(self, route: Route):
        route_annotation = route.method.annotations.get_one_or_none(RouteAnnotation)

        if route_annotation is None or route_annotation.produces is None:
            return self.get_produces()
        return [str(media_type) for media_type in route_annotation.produces]

    def _get_request_body_parameters(self, route: Route) -> List[openapi.Parameter]:
        method = route.method
        input_serializer = method.annotations.get_one_or_none(InputSerializer)
        if input_serializer is not None:
            serializer = input_serializer.class_()
            schema = self.get_request_body_schema(serializer)
            return [openapi.Parameter(name='data', in_=openapi.IN_BODY, required=True, schema=schema)]
        request_body_annotation = method.annotations.get_one_or_none(RequestBodyAnnotation)

        if request_body_annotation is not None:
            argument = method.get_argument(request_body_annotation.argument_name)
            type_info = inspect_type(argument.type_)
            title = get_schema_title(argument)
            schema = openapi.Schema(title=title, **type_info.as_dict())
            return [openapi.Parameter(name='data', in_=openapi.IN_BODY, required=True, schema=schema)]
        return []

    def _get_route(self) -> Optional[Route]:
        view_cls = type(self.view)
        func = getattr(view_cls, self.method.lower(), None)
        return getattr(func, 'route', None)
