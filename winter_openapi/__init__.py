from enum import Enum

from winter.data.pagination import Page
from winter.web.pagination.limits import MaximumLimitValueExceeded
from .annotations import global_exception
from .annotations import register_global_exception
from .enum_inspector import inspect_enum_class
from .route_parameters_inspector import RouteParametersInspector
from .route_parameters_inspector import get_route_parameters_inspectors
from .route_parameters_inspector import register_route_parameters_inspector
from .page_position_argument_inspector import PagePositionArgumentsInspector
from .path_parameters_inspector import PathParametersInspector
from .query_parameters_inspector import QueryParametersInspector
from .swagger_auto_schema import SwaggerAutoSchema
from .type_inspection import InspectorNotFound
from .type_inspection import TypeInfo
from .type_inspection import inspect_type
from .type_inspection import register_type_inspector
from .validators import validate_missing_raises_annotations


def setup(allow_missing_raises_annotation: bool = False):
    from drf_yasg.inspectors.field import hinting_type_info
    from .page_inspector import inspect_page

    register_global_exception(MaximumLimitValueExceeded)
    hinting_type_info.insert(0, (Enum, inspect_enum_class))
    register_type_inspector(Page, func=inspect_page)
    register_route_parameters_inspector(PathParametersInspector())
    register_route_parameters_inspector(QueryParametersInspector())
    if not allow_missing_raises_annotation:  # pragma: no cover
        validate_missing_raises_annotations()
