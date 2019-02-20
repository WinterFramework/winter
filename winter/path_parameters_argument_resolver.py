import uritemplate
from django.urls import get_resolver
from rest_framework.request import Request

from .argument_resolver import ArgumentResolver
from .controller import ControllerMethodArgument
from .routing import route_table


class PathParametersArgumentResolver(ArgumentResolver):
    def __init__(self):
        super().__init__()
        self._url_resolver = get_resolver()

    def is_supported(self, argument: ControllerMethodArgument) -> bool:
        route = route_table.get_method_route(argument.method)
        return argument.name in uritemplate.variables(route.url_path)

    def resolve_argument(self, argument: ControllerMethodArgument, http_request: Request):
        resolver_match = self._url_resolver.resolve(http_request.path_info)
        callback, callback_args, callback_kwargs = resolver_match
        return argument.type_(callback_kwargs[argument.name])
