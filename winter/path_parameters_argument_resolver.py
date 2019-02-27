from django.urls import get_resolver
from rest_framework.request import Request

from .argument_resolver import ArgumentResolver
from .core import ComponentMethodArgument
from .routing.routing import get_route


class PathParametersArgumentResolver(ArgumentResolver):

    def __init__(self):
        super().__init__()
        self._url_resolver = get_resolver()

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        route = get_route(argument.method)
        return argument.name in route.path_variables

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):
        resolver_match = self._url_resolver.resolve(http_request.path_info)
        callback, callback_args, callback_kwargs = resolver_match
        return argument.type_(callback_kwargs[argument.name])
