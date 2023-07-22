from typing import MutableMapping

import django.http
from django.urls import get_resolver

from winter.core import ComponentMethodArgument
from .argument_resolver import ArgumentNotSupported
from .argument_resolver import ArgumentResolver
from .routing import get_route


class PathParametersArgumentResolver(ArgumentResolver):

    def __init__(self):
        super().__init__()
        self._url_resolver = get_resolver()
        self._cache = {}

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        if argument in self._cache:
            return self._cache[argument]

        route = get_route(argument.method)
        if route is None:
            return False

        path_variables = route.get_path_variables()
        is_supported = self._cache[argument] = argument.name in path_variables
        return is_supported

    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: django.http.HttpRequest,
        response_headers: MutableMapping[str, str],
    ):
        resolver_match = self._url_resolver.resolve(request.path_info)
        callback, callback_args, callback_kwargs = resolver_match

        if argument.name not in callback_kwargs:
            raise ArgumentNotSupported(argument)

        return argument.type_(callback_kwargs[argument.name])
