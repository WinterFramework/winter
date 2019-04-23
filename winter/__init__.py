from . import django
from .argument_resolver import ArgumentResolver
from .argument_resolver import ArgumentsResolver
from .argument_resolver import GenericArgumentResolver
from .argument_resolver import arguments_resolver
from .controller import controller
from .drf import BodyWithContext
from .drf import input_serializer
from .drf import no_authentication
from .drf import output_serializer
from .drf import output_template
from .exceptions import RedirectException
from .exceptions.handlers import ExceptionHandler
from .exceptions.handlers import RedirectExceptionHandler
from .exceptions.handlers import exceptions_handler
from .exceptions.throws import throws
from .output_processor import register_output_processor_resolver
from .pagination import PagePositionArgumentResolver
from .pagination.page import PageOutputProcessorResolver
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
    from .path_parameters_argument_resolver import PathParametersArgumentResolver
    from .query_parameter import QueryParameterResolver
    from .drf import DRFBodyArgumentResolver
    from .drf import HttpRequestArgumentResolver
    from .schema import PathParametersInspector
    from .schema import QueryParametersInspector
    from .schema import register_controller_method_inspector
    from . import schema
    from . import pagination

    arguments_resolver.add_argument_resolver(DRFBodyArgumentResolver())
    arguments_resolver.add_argument_resolver(QueryParameterResolver())
    arguments_resolver.add_argument_resolver(PathParametersArgumentResolver())
    arguments_resolver.add_argument_resolver(PagePositionArgumentResolver())
    arguments_resolver.add_argument_resolver(HttpRequestArgumentResolver())
    register_controller_method_inspector(PathParametersInspector())
    register_controller_method_inspector(QueryParametersInspector())
    register_output_processor_resolver(PageOutputProcessorResolver())
    exceptions_handler.add_handler(RedirectException, RedirectExceptionHandler, auto_handle=True)
    schema.setup()
    pagination.setup()


_default_configuration()
