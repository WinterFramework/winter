import inspect
from typing import MutableMapping

from rest_framework.request import Request as HttpRequest

from winter.core import ComponentMethodArgument
from winter.web.argument_resolver import ArgumentResolver


class HttpRequestArgumentResolver(ArgumentResolver):

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return inspect.isclass(argument.type_) and issubclass(argument.type_, HttpRequest)

    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: HttpRequest,
        response_headers: MutableMapping[str, str],
    ):
        return request
