import inspect
import types
import typing

from .component import Component
from .component import is_component
from .component_method import ComponentMethod


def annotations(value: typing.Any) -> typing.Callable:
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

        values = method_or_component.annotations.setdefault(value.__class__, [])
        values.append(value)

        if isinstance(method_or_component, Component):
            return method_or_component.component_cls
        return method_or_component

    return wrapper
