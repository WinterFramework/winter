import abc
import typing
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

    def __init__(self):
        self._cache: typing.Dict[ComponentMethodArgument, typing.Any] = {}
        super().__init__()

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

    def add_argument_resolver(self, argument_resolver: ArgumentResolver):
        self._argument_resolvers.append(argument_resolver)

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        # ArgumentsResolver must resolve all arguments
        return True

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request) -> Any:

        if argument in self._cache:
            argument_resolver = self._cache[argument]
            return argument_resolver.resolve_argument(argument, http_request)

        for argument_resolver in self._argument_resolvers:
            if argument_resolver.is_supported(argument):
                self._cache[argument] = argument_resolver
                return argument_resolver.resolve_argument(argument, http_request)
        raise ArgumentNotSupported(argument)

    def resolve_arguments(
            self,
            method: ComponentMethod,
            http_request: Request,
    ) -> Dict[str, Any]:
        resolved_arguments = {}
        for argument in method.arguments:
            resolved_arguments[argument.name] = self.resolve_argument(argument, http_request)

        return resolved_arguments


class GenericArgumentResolver(ArgumentResolver):

    def __init__(self, arg_name: str, arg_type: Type, resolve_argument: Callable):
        self._arg_name = arg_name
        self._arg_type = arg_type
        self._resolve_argument = resolve_argument
        super().__init__()

    def is_supported(self, argument: ComponentMethodArgument) -> bool:
        return argument.name == self._arg_name and argument.type_ == self._arg_type

    def resolve_argument(self, argument: ComponentMethodArgument, http_request: Request):
        return self._resolve_argument(argument, http_request)


arguments_resolver = ArgumentsResolver()
