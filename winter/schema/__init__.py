from enum import Enum

from .enum_inspector import inspect_enum_class
from .generation import disable_generating_swagger
from .generation import enable_generating_swagger
from .generation import generate_swagger_for_operation
from .generation import is_generating_swagger_enabled
from .method_arguments_inspector import MethodArgumentsInspector
from .method_arguments_inspector import get_method_arguments_inspectors
from .method_arguments_inspector import register_controller_method_inspector
from .path_parameters_inspector import PathParametersInspector
from .query_parameters_inspector import QueryParametersInspector
from .type_inspection import register_type_inspector


def setup():
    from drf_yasg.inspectors.field import hinting_type_info
    hinting_type_info.insert(0, (Enum, inspect_enum_class))
