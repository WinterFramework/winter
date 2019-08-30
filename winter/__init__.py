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
from .exceptions.handlers import exception_handlers_registry
from .exceptions.throws import throws
from .http import ResponseEntity
from .http import request_body
from .http import response_header
from .http import response_status
from .http.exception_handlers import RedirectExceptionHandler
from .http.response_header_serializer import response_headers_serializer
from .output_processor import register_output_processor_resolver
from .pagination import PagePositionArgumentResolver
from .routing import route
from .routing import route_delete
from .routing import route_get
from .routing import route_patch
from .routing import route_post
from .routing import route_put
from .routing.query_parameters import map_query_parameter


def _default_configuration():
    from . import schema
    from . import pagination

    _add_argument_resolvers()
    _add_response_header_serializers()
    _register_controller_method_inspectors()
    _register_output_processor_resolvers()
    _add_exception_handlers()

    schema.setup()
    pagination.setup()


def _add_argument_resolvers():
    from .routing import PathParametersArgumentResolver
    from .routing import QueryParameterArgumentResolver
    from .drf import DRFBodyArgumentResolver
    from .drf import HttpRequestArgumentResolver
    from .http import RequestBodyArgumentResolver
    from .http import ResponseHeaderArgumentResolver

    arguments_resolver.add_argument_resolver(DRFBodyArgumentResolver())
    arguments_resolver.add_argument_resolver(RequestBodyArgumentResolver())
    arguments_resolver.add_argument_resolver(ResponseHeaderArgumentResolver())
    arguments_resolver.add_argument_resolver(QueryParameterArgumentResolver())
    arguments_resolver.add_argument_resolver(PathParametersArgumentResolver())
    arguments_resolver.add_argument_resolver(PagePositionArgumentResolver())
    arguments_resolver.add_argument_resolver(HttpRequestArgumentResolver())


def _add_response_header_serializers():
    from .http.response_header_serializers import DateTimeResponseHeaderSerializer
    from .http.response_header_serializers import LastModifiedResponseHeaderSerializer

    response_headers_serializer.add_serializer(DateTimeResponseHeaderSerializer())
    response_headers_serializer.add_serializer(LastModifiedResponseHeaderSerializer())


def _register_controller_method_inspectors():
    from .schema import PathParametersInspector
    from .schema import QueryParametersInspector
    from .schema import register_controller_method_inspector

    register_controller_method_inspector(PathParametersInspector())
    register_controller_method_inspector(QueryParametersInspector())


def _register_output_processor_resolvers():
    from .pagination.page import PageOutputProcessorResolver

    register_output_processor_resolver(PageOutputProcessorResolver())


def _add_exception_handlers():
    from .http.exception_handlers import ConvertExceptionHandler
    from .converters import ConvertException

    exception_handlers_registry.add_handler(ConvertException, ConvertExceptionHandler, auto_handle=True)
    exception_handlers_registry.add_handler(RedirectException, RedirectExceptionHandler, auto_handle=True)


_default_configuration()
