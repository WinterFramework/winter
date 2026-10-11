from typing import MutableMapping


from winter.web.request import Request
from winter.components import ComponentMethodArgument
from .argument_resolver import ArgumentNotSupported
from .argument_resolver import ArgumentResolver
from .routing import get_route


class PathParametersArgumentResolver(ArgumentResolver):

    def __init__(self):
        super().__init__()
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
        request: Request,
        response_headers: MutableMapping[str, str],
    ):
        if argument.name not in request.path_parameters:
            raise ArgumentNotSupported(argument)

        return argument.type_(request.path_parameters[argument.name])
