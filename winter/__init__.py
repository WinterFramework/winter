from . import django
from .argument_resolver import ArgumentResolver
from .argument_resolver import ArgumentsResolver
from .argument_resolver import GenericArgumentResolver
from .argument_resolver import arguments_resolver
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
from .routing import route_put


def _default_configuration():
    from .query_parameter import QueryParameterResolver
    from .drf import DRFBodyArgumentResolver
    from .drf import HttpRequestArgumentResolver
    from .schema import PathParametersInspector
    from .schema import QueryParametersInspector
    from .schema import register_controller_method_inspector

    arguments_resolver.add_argument_resolver(DRFBodyArgumentResolver())
    arguments_resolver.add_argument_resolver(QueryParameterResolver())
    arguments_resolver.add_argument_resolver(HttpRequestArgumentResolver())
    register_controller_method_inspector(PathParametersInspector())
    register_controller_method_inspector(QueryParametersInspector())


_default_configuration()
