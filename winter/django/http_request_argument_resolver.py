import inspect
from typing import MutableMapping

import django.http

from winter.components import ComponentMethodArgument
from winter.web import Request
from winter.web.argument_resolver import ArgumentResolver
from .request import DjangoRequest


class HttpRequestArgumentResolver(ArgumentResolver):
    """Resolves arguments annotated with Django's HttpRequest to the underlying Django request."""

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return inspect.isclass(argument.type_) and issubclass(argument.type_, django.http.HttpRequest)

    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: Request,
        response_headers: MutableMapping[str, str],
    ):
        assert isinstance(request, DjangoRequest), 'HttpRequestArgumentResolver works with the Django adapter only'
        return request.django_request
