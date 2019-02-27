import inspect
import types
import typing

from .component import Component
from .component_method import ComponentMethod


def annotate(annotation: typing.Any, *, unique=False, single=False)-> typing.Callable:
    def wrapper(
            func_or_cls: typing.Union[typing.Type, types.FunctionType, ComponentMethod]
    ) -> typing.Union[typing.Type, ComponentMethod]:

        if isinstance(func_or_cls, ComponentMethod) or isinstance(func_or_cls, types.FunctionType):
            decorator = annotate_method(annotation, unique=unique, single=single)
        elif inspect.isclass(func_or_cls):
            decorator = annotate_class(annotation, unique=unique, single=single)
        else:
            raise ValueError(f'Need function or class. Got: {func_or_cls}')
        return decorator(func_or_cls)
    return wrapper


def annotate_class(annotation: typing.Any, *, unique=False, single=False) -> typing.Callable:
    def wrapper(cls: typing.Type) -> typing.Type:
        component = Component.get_by_cls(cls)
        if annotation is not None:
            component.annotations.add(annotation, unique=unique, single=single)
        return cls

    return wrapper


def annotate_method(annotation: typing.Any, *, unique=False, single=False) -> typing.Callable:
    def wrapper(func_or_method: typing.Union[types.FunctionType, ComponentMethod]) -> ComponentMethod:
        if isinstance(func_or_method, ComponentMethod):
            method = func_or_method
        elif isinstance(func_or_method, types.FunctionType):
            method = ComponentMethod(func_or_method)
        else:
            raise ValueError(f'Need function. Got: {func_or_method}')
        if annotation is not None:
            method.annotations.add(annotation, unique=unique, single=single)
        return method
    return wrapper
