from winter.web import arguments_resolver
from . import json_encoders  # noqa: F401  registers the Django lazy string encoder
from .http_request_argument_resolver import HttpRequestArgumentResolver
from .output_template import output_template
from .view import create_django_urls_from_routes


def setup():
    arguments_resolver.add_argument_resolver(HttpRequestArgumentResolver())
