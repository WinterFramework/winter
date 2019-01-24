from . import django
from .argument_resolver import ArgumentResolver
from .argument_resolver import GenericArgumentResolver
from .argument_resolver import register_argument_resolver
from .controller import controller
from .drf import BodyWithContext
from .drf import input_serializer
from .drf import output_serializer
from .drf import output_template
from .output_processor import register_output_processor_resolver
from .query_parameter import query_parameter
from .response_entity import ResponseEntity
from .response_status import response_status
from .routing import route
from .routing import route_delete
from .routing import route_get
from .routing import route_patch
from .routing import route_post


def _default_configuration():
    from .dataclasses import DataclassesOutputProcessorResolver
    from .query_parameter import QueryParameterResolver
    from .drf import DRFBodyArgumentResolver
    from .drf import HttpRequestArgumentResolver
    from .schema import PathParametersInspector
    from .schema import QueryParametersInspector
    from .schema import register_controller_method_inspector

    register_argument_resolver(DRFBodyArgumentResolver())
    register_argument_resolver(QueryParameterResolver())
    register_argument_resolver(HttpRequestArgumentResolver())
    register_output_processor_resolver(DataclassesOutputProcessorResolver())
    register_controller_method_inspector(PathParametersInspector())
    register_controller_method_inspector(QueryParametersInspector())


_default_configuration()
