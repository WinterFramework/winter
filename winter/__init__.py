from .exceptions import RedirectException
from .exceptions import ThrottleException
from .exceptions.handlers import ExceptionHandler
from .exceptions.handlers import exception_handlers_registry
from .exceptions.throws import throws
from .routing import route
from .routing import route_delete
from .routing import route_get
from .routing import route_patch
from .routing import route_post
from .routing import route_put
from .routing.query_parameters import map_query_parameter
from .web import ResponseEntity
from .web import controller
from .web import request_body
from .web import response_header
from .web import response_status
from .web.argument_resolver import ArgumentResolver
from .web.argument_resolver import ArgumentsResolver
from .web.argument_resolver import GenericArgumentResolver
from .web.argument_resolver import arguments_resolver
from .web.exception_handlers import ThrottleExceptionHandler
from .web import arguments_resolver
from .web.output_processor import register_output_processor_resolver
from .web.response_header_serializer import response_headers_serializer


def setup():
    from . import schema
    from . import web
    from . import drf

    web.setup()
    drf.setup()
    schema.setup()


setup()
