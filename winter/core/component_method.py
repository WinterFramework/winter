import inspect
import typing
from types import FunctionType

from winter.core.state_key import StateKey

if typing.TYPE_CHECKING:
    from .component_method_atgument import ComponentMethodArgument


class ComponentMethod:

    def __init__(self, func: FunctionType):
        self.func = func
        self._controller_cls: FunctionType = None
        self._name: str = None
        self._state = {}

        type_hints = typing.get_type_hints(func)
        self.return_value_type = type_hints.pop('return', None)
        self._arguments = self._build_arguments(type_hints)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.func

    def __set_name__(self, owner: typing.Type, name: str):
        self._controller_cls = owner
        self._name = name

    def update_state(self, state_key: StateKey, state_value: typing.Any):
        if not state_key.many:
            self._state[state_key] = state_value
        else:
            items = self._state.setdefault(state_key, [])
            items.append(state_value)

    def get_state(self, state_key: StateKey):
        return self._state[state_key]

    @property
    def name(self) -> str:
        return self.func.__name__

    @property
    def arguments(self) -> typing.List['ComponentMethodArgument']:
        return list(self._arguments.values())

    def get_argument(self, name: str) -> typing.Optional['ComponentMethodArgument']:
        return self._arguments.get(name)

    @property
    def signature(self) -> inspect.Signature:
        return inspect.signature(self.func)

    def _build_arguments(self, argument_type_hints: dict):
        arguments = {
            arg_name: ComponentMethodArgument(self, arg_name, arg_type)
            for arg_name, arg_type in argument_type_hints.items()
        }
        return arguments
