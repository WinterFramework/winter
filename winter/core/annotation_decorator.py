import inspect
import types
import typing

from .component import Component
from .component_method import ComponentMethod


def annotate(
        annotation: typing.Any,
        func_or_cls: typing.Optional[typing.Union[types.FunctionType, ComponentMethod, typing.Type]] = None
) -> typing.Union[typing.Type, ComponentMethod]:
    if func_or_cls is None:
        return lambda func_or_cls_: annotate(annotation, func_or_cls_)

    if isinstance(func_or_cls, ComponentMethod) or isinstance(func_or_cls, types.FunctionType):
        return annotate_method(annotation, func_or_cls)
    elif inspect.isclass(func_or_cls):
        return annotate_class(annotation, func_or_cls)
    else:
        raise ValueError(f'Need function or class. Got: {func_or_cls}')


def annotate_class(
        value: typing.Any,
        cls: typing.Optional[ComponentMethod] = None
) -> typing.Type:
    if cls is None:
        return lambda cls_: annotate_class(value, cls_)

    component = Component.get_by_cls(cls)

    component.annotations.add(value)

    return cls


def annotate_method(
        annotation: typing.Any,
        func_or_method: typing.Optional[typing.Union[types.FunctionType, ComponentMethod]] = None
) -> ComponentMethod:
    if func_or_method is None:
        return lambda func_or_method_: annotate_method(annotation, func_or_method_)

    if isinstance(func_or_method, ComponentMethod):
        method = func_or_method
    else:
        method = ComponentMethod(func_or_method)

    method.annotations.add(annotation)

    return method
