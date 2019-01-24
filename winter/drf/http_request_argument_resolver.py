from rest_framework.request import Request as HttpRequest

from ..argument_resolver import ArgumentResolver
from ..controller import ControllerMethodArgument


class HttpRequestArgumentResolver(ArgumentResolver):
    def is_supported(self, argument: ControllerMethodArgument) -> bool:
        return issubclass(argument.type_, HttpRequest)

    def resolve_argument(self, argument: ControllerMethodArgument, http_request: HttpRequest):
        return http_request
