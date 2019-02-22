import inspect
import types
import typing

from .component import Component
from .component_method import ComponentMethod


def annotate(annotation: typing.Any) -> typing.Union[typing.Type, ComponentMethod]:

    def wrapper(func_or_cls):

        if isinstance(func_or_cls, ComponentMethod) or isinstance(func_or_cls, types.FunctionType):
            return annotate_method(annotation)(func_or_cls)
        elif inspect.isclass(func_or_cls):
            return annotate_class(annotation)(func_or_cls)
        else:
            raise ValueError(f'Need function or class. Got: {func_or_cls}')
    return wrapper


def annotate_class(value: typing.Any) -> typing.Type:

    def wrapper(cls):
        component = Component.get_by_cls(cls)
        component.annotations.add(value)
        return cls

    return wrapper


def annotate_method(annotation: typing.Any) -> ComponentMethod:

    def wrapper(func_or_method):
        if isinstance(func_or_method, ComponentMethod):
            method = func_or_method
        else:
            method = ComponentMethod(func_or_method)
        method.annotations.add(annotation)
        return method
    return wrapper
