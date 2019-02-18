import uritemplate
from django.urls import get_resolver
from rest_framework.request import Request

from winter.controller import ControllerMethodArgument
from .argument_resolver import ArgumentResolver


class PathParametersArgumentResolver(ArgumentResolver):
    def __init__(self):
        self._url_resolver = get_resolver()

    def is_supported(self, argument: ControllerMethodArgument) -> bool:
        return argument.name in uritemplate.variables(argument.method.url_path)

    def resolve_argument(self, argument: ControllerMethodArgument, http_request: Request):
        resolver_match = self._url_resolver.resolve(http_request.path_info)
        callback, callback_args, callback_kwargs = resolver_match
        return argument.type_(callback_kwargs[argument.name])
