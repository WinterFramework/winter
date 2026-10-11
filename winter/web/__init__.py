import importlib

from . import pagination
from .argument_resolver import ArgumentResolver
from .argument_resolver import ArgumentsResolver
from .argument_resolver import arguments_resolver
from .autodiscovery import find_package_routes
from .exceptions import ExceptionHandler
from .exceptions import exception_handlers_registry
from .exceptions import problem
from .exceptions.raises import raises
from .interceptor import Interceptor
from .interceptor import InterceptorRegistry
from .interceptor import interceptor_registry
from .media_type import InvalidMediaTypeException
from .media_type import MediaType
from .output_processor import register_output_processor_resolver
from .query_parameters import map_query_parameter
from .query_parameters import query_parameters
from .request_body_annotation import request_body
from .request import Request
from .request_body_resolver import RequestBodyArgumentResolver
from .request_handler import handle_request
from .request_handler import register_native_response_type
from .request_header_annotation import request_header
from .response import Response
from .response_entity import ResponseEntity
from .response_header_annotation import ResponseHeader
from .response_header_annotation import response_header
from .response_header_resolver import ResponseHeaderArgumentResolver
from .response_header_serializer import response_headers_serializer
from .response_status_annotation import response_status
from .routing import route
from .routing import route_delete
from .routing import route_get
from .routing import route_patch
from .routing import route_post
from .routing import route_put
from .throttling import InMemoryThrottlingStorage
from .throttling import ThrottlingMisconfigurationException
from .throttling import ThrottlingStorage
from .throttling import set_throttling_storage
from .throttling import throttling
from .urls import register_url_regexp


def setup():
    from .exceptions import RedirectException
    from .exceptions.problem_handling import autodiscover_problem_annotations
    from .exceptions.problem_handling import ProblemExceptionHandlerGenerator
    from .exceptions.problem_handling import ProblemExceptionMapper
    from .exceptions.problem_handling_info import ProblemHandlingInfo
    from .exception_handlers import RedirectExceptionHandler
    from .pagination.page_processor_resolver import PageOutputProcessorResolver
    from .pagination.page_position_argument_resolver import PagePositionArgumentResolver
    from .path_parameters_argument_resolver import PathParametersArgumentResolver
    from .query_parameters.query_parameter_argument_resolver import QueryParameterArgumentResolver
    from .query_parameters.query_parameters_argument_resolver import QueryParametersArgumentResolver
    from .request_argument_resolver import RequestArgumentResolver
    from .request_header_resolver import RequestHeaderArgumentResolver
    from .response_header_serializers import DateTimeResponseHeaderSerializer
    from .response_header_serializers import LastModifiedResponseHeaderSerializer

    register_output_processor_resolver(PageOutputProcessorResolver())
    response_headers_serializer.add_serializer(DateTimeResponseHeaderSerializer())
    response_headers_serializer.add_serializer(LastModifiedResponseHeaderSerializer())
    arguments_resolver.add_argument_resolver(QueryParameterArgumentResolver())
    arguments_resolver.add_argument_resolver(QueryParametersArgumentResolver())
    arguments_resolver.add_argument_resolver(PathParametersArgumentResolver())
    arguments_resolver.add_argument_resolver(RequestBodyArgumentResolver())
    arguments_resolver.add_argument_resolver(ResponseHeaderArgumentResolver())
    arguments_resolver.add_argument_resolver(PagePositionArgumentResolver())
    arguments_resolver.add_argument_resolver(RequestHeaderArgumentResolver())
    arguments_resolver.add_argument_resolver(RequestArgumentResolver())

    exception_mapper = ProblemExceptionMapper()
    exception_handler_generator = ProblemExceptionHandlerGenerator(exception_mapper)
    autodiscover_problem_annotations(exception_handler_generator)
    exception_handlers_registry.add_handler(RedirectException, RedirectExceptionHandler, auto_handle=True)


def __getattr__(name):
    # Deprecated since 33.0, removed in 34.0: the Redis storage lives in the winter.redis adapter.
    # The subpackage is imported by name because `throttling` in this namespace is the decorator.
    throttling_package = importlib.import_module('winter.web.throttling')
    if name in throttling_package._DEPRECATED_REDIS_NAMES:
        return getattr(throttling_package, name)
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
