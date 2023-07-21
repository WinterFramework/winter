import inspect
from typing import MutableMapping

import django.http

from winter.core import ComponentMethodArgument
from winter.web.argument_resolver import ArgumentResolver


class HttpRequestArgumentResolver(ArgumentResolver):

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return inspect.isclass(argument.type_) and issubclass(argument.type_, django.http.HttpRequest)

    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: django.http.HttpRequest,
        response_headers: MutableMapping[str, str],
    ):
        return request
