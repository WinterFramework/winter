import types
import typing

from .component import Component
from .component_method import ComponentMethod
from .state_key import StateKey


class WinterApplication:

    def __init__(self):
        self._components = {}

    @property
    def components(self):
        return types.MappingProxyType(self._components)

    def component(self, cls: typing.Type):
        self._components[cls] = Component(cls)
        return cls

    def component_method(
            self,
            func: typing.Union[types.FunctionType, ComponentMethod],
            state_key: StateKey = None,
            state_value: typing.Any = None
    ):

        if isinstance(func, ComponentMethod):
            method = func
        else:
            method = ComponentMethod(func)

        if state_key is None:
            return method

        method.update_state(state_key, state_value)

        return method
