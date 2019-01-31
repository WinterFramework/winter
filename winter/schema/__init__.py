from enum import Enum

from .controller_method_inspector import ControllerMethodInspector
from .controller_method_inspector import get_controller_method_inspectors
from .controller_method_inspector import register_controller_method_inspector
from .enum_inspector import inspect_enum_class
from .generation import generate_swagger_for_operation
from .path_parameters_inspector import PathParametersInspector
from .query_parameters_inspector import QueryParametersInspector


def setup():
    from drf_yasg.inspectors.field import hinting_type_info
    hinting_type_info.append((Enum, inspect_enum_class))
