import typing
from abc import ABCMeta
from abc import abstractmethod
from typing import Callable
from typing import Dict
from typing import Type

from rest_framework.request import Request

from .controller import ControllerMethod
from .controller import ControllerMethodArgument

_resolvers = []


class ArgumentResolver(metaclass=ABCMeta):
    """IArgumentResolver is used to map http request contents to controller method arguments."""
    @abstractmethod
    def is_supported(self, argument: ControllerMethodArgument) -> bool:
        return False

    @abstractmethod
    def resolve_argument(self, argument: ControllerMethodArgument, http_request: Request):
        return None


class GenericArgumentResolver(ArgumentResolver):
    def __init__(self, arg_name: str, arg_type: Type, resolve_argument: Callable):
        self._arg_name = arg_name
        self._arg_type = arg_type
        self._resolve_argument = resolve_argument

    def is_supported(self, argument: ControllerMethodArgument) -> bool:
        return argument.name == self._arg_name and argument.type_ == self._arg_type

    def resolve_argument(self, argument: ControllerMethodArgument, http_request: Request):
        return self._resolve_argument(http_request)


def register_argument_resolver(resolver: ArgumentResolver):
    _resolvers.append(resolver)


def resolve_arguments(
        controller_method: ControllerMethod,
        http_request: Request,
        path_variables: Dict,
) -> Dict[str, object]:
    type_hints = typing.get_type_hints(controller_method.func)
    type_hints.pop('return', None)
    resolved_arguments = {}
    for argument in controller_method.arguments:
        resolver = find_resolver(argument)
        if resolver:
            resolved_arguments[argument.name] = resolver.resolve_argument(argument, http_request)
            continue
        if argument.name in path_variables:
            str_value = path_variables[argument.name]
            resolved_arguments[argument.name] = argument.type_(str_value)
            continue
        raise Exception(f'Cant resolve argument {argument.name}: {argument.type_}')
    return resolved_arguments


def find_resolver(argument: ControllerMethodArgument) -> typing.Optional[ArgumentResolver]:
    for resolver in _resolvers:
        if resolver.is_supported(argument):
            return resolver
    return None
