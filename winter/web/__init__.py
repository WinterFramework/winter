from . import pagination
from .argument_resolver import arguments_resolver
from .controller import controller
from .exception_handlers import DecodeExceptionHandler
from .media_type import InvalidMediaTypeException
from .media_type import MediaType
from .output_processor import register_output_processor_resolver
from .request_body_annotation import request_body
from .request_body_resolver import RequestBodyArgumentResolver
from .response_entity import ResponseEntity
from .response_header_annotation import ResponseHeader
from .response_header_annotation import response_header
from .response_header_resolver import ResponseHeaderArgumentResolver
from .response_header_serializer import response_headers_serializer
from .response_status_annotation import response_status
from .throttling import throttling
from .urls import register_url_regexp


def setup():
    from winter.core.json.decoder import JSONDecodeException
    from winter.exceptions.handlers import exception_handlers_registry
    from winter.exceptions import RedirectException
    from winter.exceptions import ThrottleException
    from .exception_handlers import BadRequestExceptionHandler
    from .exception_handlers import RedirectExceptionHandler
    from .exception_handlers import ThrottleExceptionHandler
    from .path_parameters_argument_resolver import PathParametersArgumentResolver
    from .query_parameters_argument_resolver import QueryParameterArgumentResolver
    from .response_header_serializers import DateTimeResponseHeaderSerializer
    from .response_header_serializers import LastModifiedResponseHeaderSerializer
    from .pagination.limits import MaximumLimitValueExceeded
    from .pagination.page_processor_resolver import PageOutputProcessorResolver
    from .pagination.page_position_argument_resolver import PagePositionArgumentResolver

    register_output_processor_resolver(PageOutputProcessorResolver())
    response_headers_serializer.add_serializer(DateTimeResponseHeaderSerializer())
    response_headers_serializer.add_serializer(LastModifiedResponseHeaderSerializer())
    arguments_resolver.add_argument_resolver(QueryParameterArgumentResolver())
    arguments_resolver.add_argument_resolver(PathParametersArgumentResolver())
    arguments_resolver.add_argument_resolver(RequestBodyArgumentResolver())
    arguments_resolver.add_argument_resolver(ResponseHeaderArgumentResolver())
    arguments_resolver.add_argument_resolver(PagePositionArgumentResolver())
    exception_handlers_registry.add_handler(JSONDecodeException, DecodeExceptionHandler, auto_handle=True)
    exception_handlers_registry.add_handler(RedirectException, RedirectExceptionHandler, auto_handle=True)
    exception_handlers_registry.add_handler(MaximumLimitValueExceeded, BadRequestExceptionHandler, auto_handle=True)
    exception_handlers_registry.add_handler(ThrottleException, ThrottleExceptionHandler, auto_handle=True)