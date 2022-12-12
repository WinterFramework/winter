import inspect
from typing import MutableMapping

from rest_framework.request import Request as HttpRequest

from winter.core import ComponentMethodArgument
from winter.core.utils.typing import NoneType
from winter.core.utils.typing import get_generic_args
from winter.core.utils.typing import is_optional
from winter.web.argument_resolver import ArgumentResolver


class HttpRequestArgumentResolver(ArgumentResolver):

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        argument_type = argument.type_
        if is_optional(argument_type):
            types = [type_ for type_ in get_generic_args(argument_type) if type_ is not NoneType]
            if len(types) != 1:
                return False
            argument_type = types[0]
        return inspect.isclass(argument_type) and issubclass(argument_type, HttpRequest)

    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: HttpRequest,
        response_headers: MutableMapping[str, str],
    ):
        return request
