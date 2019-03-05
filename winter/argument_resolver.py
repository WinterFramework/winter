import abc
from abc import abstractmethod
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Type

from rest_framework.request import Request

from .core import ComponentMethod
from .core import ComponentMethodArgument


class ArgumentNotSupported(Exception):

    def __init__(self, argument: ComponentMethodArgument):
        super().__init__(f'Unable to resolve argument {argument.name}: {argument.type_.__name__}')


class ArgumentResolver(abc.ABC):
    """IArgumentResolver is used to map http request contents to controller method arguments."""

    @abstractmethod
    def is_supported(self, argument: ComponentMethodArgument) -> bool:  # pragma: no cover
        pass

    @abstractmethod
    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):  # pragma: no cover
        pass


class ArgumentsResolver(ArgumentResolver):

    def __init__(self):
        super().__init__()
        self._argument_resolvers: List[ArgumentResolver] = []
        self._cache = {}

    def add_argument_resolver(self, argument_resolver: ArgumentResolver):
        self._argument_resolvers.append(argument_resolver)

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        # ArgumentsResolver must resolve all arguments
        return True

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request) -> Any:
        argument_resolver = self._get_argument_resolver(argument)
        return argument_resolver.resolve_argument(argument, http_request)

    def resolve_arguments(
            self,
            method: ComponentMethod,
            http_request: Request,
    ) -> Dict[str, Any]:
        resolved_arguments = {}
        for argument in method.arguments:
            resolved_arguments[argument.name] = self.resolve_argument(argument, http_request)

        return resolved_arguments

    def _get_argument_resolver(self, argument: ComponentMethodArgument) -> 'ArgumentResolver':
        if argument in self._cache:
            return self._cache[argument]
        for argument_resolver in self._argument_resolvers:
            if argument_resolver.is_supported(argument):
                self._cache[argument] = argument_resolver
                return argument_resolver
        raise ArgumentNotSupported(argument)


class GenericArgumentResolver(ArgumentResolver):

    def __init__(self, arg_name: str, arg_type: Type, resolve_argument: Callable):
        super().__init__()
        self._arg_name = arg_name
        self._arg_type = arg_type
        self._resolve_argument = resolve_argument

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return argument.name == self._arg_name and argument.type_ == self._arg_type

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):
        return self._resolve_argument(argument, http_request)


arguments_resolver = ArgumentsResolver()
