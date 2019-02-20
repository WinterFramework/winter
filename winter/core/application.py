import types
import typing

from .component import Component
from .component_method import ComponentMethod
from .metadata_key import MetadataKey


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
            metadata_key: MetadataKey = None,
            state_value: typing.Any = None
    ):

        if isinstance(func, ComponentMethod):
            method = func
        else:
            method = ComponentMethod(func)

        if metadata_key is None:
            return method

        method.update_state(metadata_key, state_value)

        return method
