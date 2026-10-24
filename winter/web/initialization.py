from .argument_resolver import arguments_resolver
from .output_processor import register_output_processor_resolver
from .pagination.page_position_argument_resolver import PagePositionArgumentResolver
from .pagination.page_processor_resolver import PageOutputProcessorResolver
from .path_parameters_argument_resolver import PathParametersArgumentResolver
from .query_parameters.query_parameter_argument_resolver import QueryParameterArgumentResolver
from .query_parameters.query_parameters_argument_resolver import QueryParametersArgumentResolver
from .request_argument_resolver import RequestArgumentResolver
from .request_body_resolver import RequestBodyArgumentResolver
from .request_header_resolver import RequestHeaderArgumentResolver
from .response_header_resolver import ResponseHeaderArgumentResolver
from .response_header_serializer import response_headers_serializer
from .response_header_serializers import DateTimeResponseHeaderSerializer
from .response_header_serializers import LastModifiedResponseHeaderSerializer

_process_initialized = False


def initialize():
    """
    Registers the standard resolvers of winter.web on the first call. Adapters call it before building their routes.
    Process-global until the registries move into Application: docs/architecture.md, Current deviations.
    """
    global _process_initialized
    if not _process_initialized:
        _initialize_process()
        _process_initialized = True


def _initialize_process():
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
