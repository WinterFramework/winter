from enum import Enum

from winter.data.pagination import Page
from winter.web.exceptions import RequestDataDecodeException
from winter.web.exceptions import ThrottleException
from winter.web.pagination.limits import MaximumLimitValueExceeded
from .annotations import global_exception
from .annotations import register_global_exception
from .inspectors import inspect_enum_class
from .inspectors import RouteParametersInspector
from .inspectors import get_route_parameters_inspectors
from .inspectors import register_route_parameters_inspector
from .inspectors import PagePositionArgumentsInspector
from .inspectors import PathParametersInspector
from .inspectors import QueryParametersInspector
from .swagger_auto_schema import SwaggerAutoSchema
from .swagger_ui import get_swagger_ui_html
from .type_inspection import InspectorNotFound
from .type_inspection import TypeInfo
from .type_inspection import inspect_type
from .type_inspection import register_type_inspector
from .validators import validate_missing_raises_annotations


def setup(allow_missing_raises_annotation: bool = False):
    from drf_yasg.inspectors.field import hinting_type_info
    from .inspectors.page_inspector import inspect_page

    register_global_exception(MaximumLimitValueExceeded)
    register_global_exception(ThrottleException)
    register_global_exception(RequestDataDecodeException)
    hinting_type_info.insert(0, (Enum, inspect_enum_class))
    register_type_inspector(Page, func=inspect_page)
    register_route_parameters_inspector(PathParametersInspector())
    register_route_parameters_inspector(QueryParametersInspector())
    if not allow_missing_raises_annotation:  # pragma: no cover
        validate_missing_raises_annotations()
