from typing import List

from openapi_schema_pydantic.v3.v3_0_3 import Parameter
from openapi_schema_pydantic.v3.v3_0_3 import Schema

from winter.data.pagination import PagePosition
from winter.web.pagination.order_by import OrderByAnnotation
from winter.web.pagination.page_position_argument_resolver import PagePositionArgumentResolver
from winter.web.routing import Route
from winter_openapi.inspection.data_types import DataTypes
from .route_parameters_inspector import RouteParametersInspector


class PagePositionArgumentsInspector(RouteParametersInspector):
    def __init__(self, page_position_argument_resolver: PagePositionArgumentResolver):
        self._page_position_argument_resolver = page_position_argument_resolver
        self.limit_parameter = Parameter(
            name=page_position_argument_resolver.limit_name,
            description='Number of results to return per page',
            required=False,
            param_in="query",
            type=DataTypes.INTEGER,
            param_schema=Schema(type=DataTypes.INTEGER),
        )
        self.offset_parameter = Parameter(
            name=page_position_argument_resolver.offset_name,
            description='The initial index from which to return the results',
            required=False,
            param_in="query",
            type=DataTypes.INTEGER,
            param_schema=Schema(type=DataTypes.INTEGER)
        )

    def inspect_parameters(self, route: 'Route') -> List[Parameter]:
        parameters = []
        has_page_position_argument = any(argument.type_ == PagePosition for argument in route.method.arguments)
        if not has_page_position_argument:
            return []

        parameters.append(self.limit_parameter)
        parameters.append(self.offset_parameter)

        order_by_annotation = route.method.annotations.get_one_or_none(OrderByAnnotation)
        if order_by_annotation:
            allowed_order_by_fields = ','.join(map(str, order_by_annotation.allowed_fields))
            default_sort = (
                [str(order_by_annotation.default_sort)]
                if order_by_annotation.default_sort is not None else
                None
            )
            order_by_parameter = Parameter(
                name=self._page_position_argument_resolver.order_by_name,
                description=f'Comma separated order by fields. Allowed fields: {allowed_order_by_fields}.',
                required=False,
                param_in="query",
                param_schema=Schema(
                    type=DataTypes.ARRAY,
                    default=default_sort,
                    items=Schema(
                        type=DataTypes.STRING,
                    )
                ),
            )
            parameters.append(order_by_parameter)

        return parameters
