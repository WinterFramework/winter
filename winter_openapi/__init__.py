from enum import Enum

from winter.data.pagination import Page
from winter.web.pagination.limits import MaximumLimitValueExceeded
from .annotations import global_exception
from .annotations import register_global_exception
from .enum_inspector import inspect_enum_class
from .inspectors import SwaggerAutoSchema
from .method_arguments_inspector import MethodArgumentsInspector
from .method_arguments_inspector import get_method_arguments_inspectors
from .method_arguments_inspector import register_controller_method_inspector
from .page_position_argument_inspector import PagePositionArgumentsInspector
from .path_parameters_inspector import PathParametersInspector
from .query_parameters_inspector import QueryParametersInspector
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
    register_controller_method_inspector(PathParametersInspector())
    register_controller_method_inspector(QueryParametersInspector())
    if not allow_missing_raises_annotation:
        validate_missing_raises_annotations()
