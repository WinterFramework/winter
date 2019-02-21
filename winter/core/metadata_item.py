import abc
import inspect
import types
import typing

from .component import Component
from .component import is_component
from .component_method import ComponentMethod


class MetadataItem(abc.ABC):
    key: str = None

    def __init_subclass__(cls, **kwargs):
        key = kwargs.pop('key', None)
        assert key is not None, 'Not given "key"'
        cls.key = key

    def __init__(self, value: typing.Any):
        self.value = value

    @abc.abstractmethod
    def set_value(self, metadata_storage: typing.Dict) -> None:
        pass


def metadata(metadata_item: MetadataItem) -> typing.Callable:
    def wrapper(func_or_cls: typing.Union[types.FunctionType, ComponentMethod]):
        if isinstance(func_or_cls, ComponentMethod):
            method_or_component = func_or_cls
        elif isinstance(func_or_cls, types.FunctionType):
            method_or_component = ComponentMethod(func_or_cls)
        elif is_component(func_or_cls):
            method_or_component = func_or_cls
        elif inspect.isclass(func_or_cls):
            method_or_component = Component.register(func_or_cls)
        else:
            raise ValueError(f'Need function or class. Got: {func_or_cls}')

        method_or_component.metadata.add(metadata_item)
        if isinstance(method_or_component, Component):
            return method_or_component.component_cls
        return method_or_component

    return wrapper
