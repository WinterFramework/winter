import abc
from abc import abstractmethod
from typing import Any
from typing import Collection
from typing import Dict
from typing import Mapping
from typing import MutableMapping
from typing import Optional
from typing import Sequence

from injector import Injector

from winter.web.request import Request
from winter.components import ComponentMethod
from winter.components import ComponentMethodArgument
from winter.typing import get_type_name
from .request_scope import is_bound


class ArgumentNotSupported(Exception):

    def __init__(self, argument: ComponentMethodArgument):
        type_name = get_type_name(argument.type_)
        super().__init__(f'Unable to resolve argument {argument.name}: {type_name}')


class ArgumentResolver(abc.ABC):
    """Maps a part of the request, such as a query parameter or the body, to the arguments that declare it."""

    @abstractmethod
    def is_supported(self, argument: ComponentMethodArgument) -> bool:  # pragma: no cover
        pass

    @abstractmethod
    def resolve_argument(
        self,
        argument: ComponentMethodArgument,
        request: Request,
        response_headers: MutableMapping[str, str],
    ):  # pragma: no cover
        pass


class ArgumentsResolver:
    """
    Resolves the arguments of a method: an argument mapped from the request by one of the resolvers is taken
    from the request, any other one from the injector of the request, which must bind its type.
    """

    def __init__(self, argument_resolvers: Sequence[ArgumentResolver]):
        self._argument_resolvers = tuple(argument_resolvers)
        self._cache: Dict[ComponentMethodArgument, Optional[ArgumentResolver]] = {}

    def check_arguments(
        self,
        method: ComponentMethod,
        app_injector: Injector,
        request_types: Collection[type],
        context_names: Collection[str] = (),
    ):
        """Fails on startup for an argument that a request would not resolve."""
        for argument in method.arguments:
            if argument.name in context_names or self._get_argument_resolver(argument) is not None:
                continue
            if argument.type_ not in request_types and not is_bound(app_injector, argument.type_):
                raise _unbound_argument(argument)

    def resolve_arguments(
        self,
        method: ComponentMethod,
        request: Request,
        response_headers: MutableMapping[str, str],
        request_injector: Injector,
        context: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        if context is None:
            context = {}
        resolved_arguments = {}
        for argument in method.arguments:
            if argument.name in context:
                resolved_arguments[argument.name] = context[argument.name]
                continue
            argument_resolver = self._get_argument_resolver(argument)
            if argument_resolver is not None:
                value = argument_resolver.resolve_argument(argument, request, response_headers)
            elif is_bound(request_injector, argument.type_):
                value = request_injector.get(argument.type_)
            else:
                raise _unbound_argument(argument)
            resolved_arguments[argument.name] = value
        return resolved_arguments

    def _get_argument_resolver(self, argument: ComponentMethodArgument) -> Optional[ArgumentResolver]:
        if argument not in self._cache:
            self._cache[argument] = next(
                (resolver for resolver in self._argument_resolvers if resolver.is_supported(argument)),
                None,
            )
        return self._cache[argument]


def _unbound_argument(argument: ComponentMethodArgument) -> TypeError:
    # Whatever the injector could create is not enough: a forgotten @request_body would become an empty object
    method = argument.method
    method_name = method.full_name if method.component is not None else method.func.__qualname__
    return TypeError(
        f'{method_name}: argument {argument.name} ({get_type_name(argument.type_)}) '
        f'is not mapped from the request and has no binding in the injector',
    )
