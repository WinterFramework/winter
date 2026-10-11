from django.http.response import HttpResponseBase

from winter.web import arguments_resolver
from winter.web import register_native_response_type
from . import json_encoders  # noqa: F401  registers the Django lazy string encoder
from .http_request_argument_resolver import HttpRequestArgumentResolver
from .output_template import output_template
from .request import DjangoRequest
from .reverse import reverse
from .view import create_django_urls_from_routes
from .view import to_django_response


def setup():
    arguments_resolver.add_argument_resolver(HttpRequestArgumentResolver())
    register_native_response_type(HttpResponseBase)
