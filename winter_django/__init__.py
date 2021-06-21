from winter.web import arguments_resolver
from .body_argument_resolver import DRFBodyArgumentResolver
from .body_with_context import BodyWithContext
from .http_request_argument_resolver import HttpRequestArgumentResolver
from .input_serializer import InputSerializer
from .input_serializer import input_serializer
from .output_serializer import get_output_serializer
from .output_serializer import output_serializer
from .output_template import output_template
from .page_serializer import PageSerializer
from .view import create_django_urls


def setup():
    arguments_resolver.add_argument_resolver(DRFBodyArgumentResolver())
    arguments_resolver.add_argument_resolver(HttpRequestArgumentResolver())
