import inspect
import types
import typing

from .component import Component
from .component_method import ComponentMethod


def annotate(
        value: typing.Any,
        func_or_cls: typing.Optional[typing.Union[types.FunctionType, ComponentMethod, typing.Type]] = None
) -> typing.Callable:
    if func_or_cls is None:
        return lambda func_or_cls: annotate(value, func_or_cls)

    if isinstance(func_or_cls, ComponentMethod) or isinstance(func_or_cls, types.FunctionType):
        return annotate_method(value, func_or_cls)
    elif inspect.isclass(func_or_cls):
        return annotate_class(value, func_or_cls)
    else:
        raise ValueError(f'Need function or class. Got: {func_or_cls}')


def annotate_class(
        value: typing.Any,
        cls: typing.Optional[ComponentMethod] = None
):
    if cls is None:
        return lambda cls: annotate_class(value, cls)

    component = Component.get_by_cls(cls)

    component.annotations.add(value)

    return cls


def annotate_method(
        value: typing.Any,
        func_or_method: typing.Optional[typing.Union[types.FunctionType, ComponentMethod]] = None
):
    if func_or_method is None:
        return lambda func_or_method: annotate_method(value, func_or_method)

    if isinstance(func_or_method, ComponentMethod):
        method = func_or_method
    else:
        method = ComponentMethod(func_or_method)

    method.annotations.add(value)

    return method
