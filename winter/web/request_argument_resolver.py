import inspect
from typing import MutableMapping

from winter.components import ComponentMethodArgument
from .argument_resolver import ArgumentResolver
from .request import Request


class RequestArgumentResolver(ArgumentResolver):

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return inspect.isclass(argument.type_) and issubclass(argument.type_, Request)

    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: Request,
        response_headers: MutableMapping[str, str],
    ):
        return request
