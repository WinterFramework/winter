from enum import Enum

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


def setup():
    from drf_yasg.inspectors.field import hinting_type_info
    from winter.data.pagination import Page
    from .page_inspector import inspect_page

    hinting_type_info.insert(0, (Enum, inspect_enum_class))
    register_type_inspector(Page, func=inspect_page)
    register_controller_method_inspector(PathParametersInspector())
    register_controller_method_inspector(QueryParametersInspector())
