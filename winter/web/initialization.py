from winter.application import Application
from .argument_resolver import arguments_resolver
from .exception_handlers import RedirectExceptionHandler
from .exceptions import RedirectException
from .exceptions import RequestDataDecodeException
from .exceptions import ThrottleException
from .exceptions import UnsupportedMediaTypeException
from .exceptions import exception_handlers_registry
from .exceptions.problem_handling import ProblemExceptionHandlerGenerator
from .exceptions.problem_handling import ProblemExceptionMapper
from .exceptions.problem_handling import add_problem_handlers
from .output_processor import register_output_processor_resolver
from .pagination.limits import MaximumLimitValueExceeded
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

_problem_handler_generator = ProblemExceptionHandlerGenerator(ProblemExceptionMapper())
_process_initialized = False


def initialize(app: Application):
    """
    Prepares winter.web to handle the requests of an application. Adapters call it before building their routes.

    The registries are still process-global: the standard resolvers are registered on the first call,
    the handlers of the application's @problem exceptions on every call.
    """
    global _process_initialized
    if not _process_initialized:
        _initialize_process()
        _process_initialized = True
    add_problem_handlers(app.definitions, _problem_handler_generator)


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
    framework_problems = [
        ThrottleException,
        RequestDataDecodeException,
        UnsupportedMediaTypeException,
        MaximumLimitValueExceeded,
    ]
    add_problem_handlers(framework_problems, _problem_handler_generator)
    exception_handlers_registry.add_handler(RedirectException, RedirectExceptionHandler, auto_handle=True)
