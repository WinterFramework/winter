from . import pagination
from .argument_resolver import arguments_resolver
from .auth import no_authentication
from .configurer import Configurer
from .controller import controller
from .controller import get_component
from .controller import get_instance
from .controller import set_factory
from .exceptions import ExceptionHandler
from .exceptions import exception_handlers_registry
from .exceptions import problem
from .interceptor import Interceptor
from .interceptor import InterceptorRegistry
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
    from winter.data.exceptions import NotFoundException
    from .configurer import run_configurers
    from .exceptions import RedirectException
    from .exceptions.problem_handling import autodiscover_problem_annotations
    from .exceptions.problem_handling import ProblemExceptionHandlerGenerator
    from .exceptions.problem_handling import ProblemExceptionMapper
    from .exceptions.problem_handling_info import ProblemHandlingInfo
    from .exception_handlers import RedirectExceptionHandler
    from .exception_handlers import DecodeExceptionHandler
    from .pagination.page_processor_resolver import PageOutputProcessorResolver
    from .pagination.page_position_argument_resolver import PagePositionArgumentResolver
    from .path_parameters_argument_resolver import PathParametersArgumentResolver
    from .query_parameters.query_parameters_argument_resolver import QueryParameterArgumentResolver
    from .response_header_serializers import DateTimeResponseHeaderSerializer
    from .response_header_serializers import LastModifiedResponseHeaderSerializer

    register_output_processor_resolver(PageOutputProcessorResolver())
    response_headers_serializer.add_serializer(DateTimeResponseHeaderSerializer())
    response_headers_serializer.add_serializer(LastModifiedResponseHeaderSerializer())
    arguments_resolver.add_argument_resolver(QueryParameterArgumentResolver())
    arguments_resolver.add_argument_resolver(PathParametersArgumentResolver())
    arguments_resolver.add_argument_resolver(RequestBodyArgumentResolver())
    arguments_resolver.add_argument_resolver(ResponseHeaderArgumentResolver())
    arguments_resolver.add_argument_resolver(PagePositionArgumentResolver())

    exception_mapper = ProblemExceptionMapper()
    exception_handler_generator = ProblemExceptionHandlerGenerator(exception_mapper)
    autodiscover_problem_annotations(exception_handler_generator)
    auto_handle_exceptions = {
        JSONDecodeException: DecodeExceptionHandler,
        RedirectException: RedirectExceptionHandler,
        NotFoundException: exception_handler_generator.generate(NotFoundException, ProblemHandlingInfo(status=404)),
    }
    for exception_class, handler in auto_handle_exceptions.items():
        exception_handlers_registry.add_handler(exception_class, handler, auto_handle=True)

    run_configurers()
