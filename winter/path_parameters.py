import itertools
from typing import List

import uritemplate
from django.urls import get_resolver
from rest_framework.request import Request

from .argument_resolver import ArgumentNotSupported
from .argument_resolver import ArgumentResolver
from .core import ComponentMethodArgument
from .routing.routing import get_url_path


class PathParametersArgumentResolver(ArgumentResolver):

    def __init__(self):
        super().__init__()
        self._url_resolver = get_resolver()
        self._cache = {}

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        if argument in self._cache:
            return self._cache[argument]

        url_path = get_url_path(argument.method)
        path_variables = self.get_path_variable_names(url_path)
        is_supported = self._cache[argument] = argument.name in path_variables
        return is_supported

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):
        resolver_match = self._url_resolver.resolve(http_request.path_info)
        callback, callback_args, callback_kwargs = resolver_match

        if argument.name not in callback_kwargs:
            raise ArgumentNotSupported(argument)

        return argument.type_(callback_kwargs[argument.name])

    @staticmethod
    def get_path_variable_names(url_path: str) -> List[str]:
        uri_template = uritemplate.URITemplate(url_path)
        path_variables = list(itertools.chain.from_iterable(
            variable.variable_names for variable in uri_template.variables if variable.operator != '?'
        ))
        return path_variables
