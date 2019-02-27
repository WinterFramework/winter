import inspect

from rest_framework.request import Request as HttpRequest

from ..argument_resolver import ArgumentResolver
from ..core import ComponentMethodArgument


class HttpRequestArgumentResolver(ArgumentResolver):

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return inspect.isclass(argument.type_) and issubclass(argument.type_, HttpRequest)

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: HttpRequest):
        return http_request
