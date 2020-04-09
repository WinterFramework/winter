from .auth import no_authentication
from .body_argument_resolver import DRFBodyArgumentResolver
from .body_with_context import BodyWithContext
from .http_request_argument_resolver import HttpRequestArgumentResolver
from .input_serializer import get_input_serializer
from .input_serializer import input_serializer
from .output_serializer import get_output_serializer
from .output_serializer import output_serializer
from .output_template import output_template


def setup():
    from . import DRFBodyArgumentResolver
    from . import HttpRequestArgumentResolver
    from winter.web import arguments_resolver

    arguments_resolver.add_argument_resolver(DRFBodyArgumentResolver())
    arguments_resolver.add_argument_resolver(HttpRequestArgumentResolver())
