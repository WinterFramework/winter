from typing import List
from typing import TYPE_CHECKING

from drf_yasg import openapi

from winter.pagination.sort import get_allowed_order_by_fields
from .page_position import PagePosition
from .page_position_argument_resolver import PagePositionArgumentResolver
from ..schema import MethodArgumentsInspector

if TYPE_CHECKING:
    from winter.routing import Route


class PagePositionArgumentsInspector(MethodArgumentsInspector):
    def __init__(self, page_position_argument_resolver: PagePositionArgumentResolver):
        self._page_position_argument_resolver = page_position_argument_resolver
        self.limit_parameter = openapi.Parameter(
            name=page_position_argument_resolver.limit_name,
            description='Number of results to return per page',
            required=False,
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
        )
        self.offset_parameter = openapi.Parameter(
            name=page_position_argument_resolver.offset_name,
            description='The initial index from which to return the results',
            required=False,
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
        )
        self.default_order_by_parameter = openapi.Parameter(
            name=page_position_argument_resolver.order_by_name,
            description='Comma separated order by fields',
            required=False,
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
        )

    def inspect_parameters(self, route: 'Route') -> List[openapi.Parameter]:
        parameters = []
        allowed_order_by_fields = get_allowed_order_by_fields(route.method)
        if not allowed_order_by_fields:
            order_by_parameter = self.default_order_by_parameter
        else:
            order_by_parameter = openapi.Parameter(
                name=self._page_position_argument_resolver.order_by_name,
                description='Comma separated order by fields',
                required=False,
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=list(allowed_order_by_fields),
            )

        for argument in route.method.arguments:
            if argument.type_ == PagePosition:
                parameters.append(self.limit_parameter)
                parameters.append(self.offset_parameter)
                parameters.append(order_by_parameter)
        return parameters
