from typing import List

from drf_yasg import openapi

from .page_position import PagePosition
from .page_position_argument_resolver import PagePositionArgumentResolver
from ..core import ComponentMethod
from ..schema import ControllerMethodInspector


class PagePositionArgumentInspector(ControllerMethodInspector):
    def __init__(self, page_position_argument_resolver: PagePositionArgumentResolver):
        self.limit_parameter = openapi.Parameter(
            name=page_position_argument_resolver.limit_parameter_name,
            description='Number of results to return per page',
            required=False,
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
        )
        self.offset_parameter = openapi.Parameter(
            name=page_position_argument_resolver.offset_parameter_name,
            description='The initial index from which to return the results',
            required=False,
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
        )

    def inspect_parameters(self, method: ComponentMethod) -> List[openapi.Parameter]:
        parameters = []
        for argument in method.arguments:
            if argument.type_ == PagePosition:
                parameters.append(self.limit_parameter)
                parameters.append(self.offset_parameter)
        return parameters
