import abc
import types
import typing

from .component import Component
from .component_method import ComponentMethod


class annotate_base(abc.ABC):
    _supported_classes = ()

    def __init__(self, annotation: typing.Any, *, unique=False, single=False):
        self.annotation = annotation
        self.unique = unique
        self.single = single

    @classmethod
    def is_supported(cls, item: typing.Any) -> bool:
        return isinstance(item, cls._supported_classes)

    @abc.abstractmethod
    def __call__(self, item) -> typing.Callable:  # pragma: no cover
        pass


class annotate(annotate_base):
    _supported_classes = (typing.Type, types.FunctionType, ComponentMethod)

    def __call__(self, func_or_cls: typing.Union[typing.Type, types.FunctionType, ComponentMethod]) -> typing.Callable:
        if annotate_method.is_supported(func_or_cls):
            decorator = annotate_method(self.annotation, unique=self.unique, single=self.single)
        elif annotate_class.is_supported(func_or_cls):
            decorator = annotate_class(self.annotation, unique=self.unique, single=self.single)
        else:
            raise ValueError(f'Need function or class. Got: {func_or_cls}')
        return decorator(func_or_cls)


class annotate_class(annotate_base):
    _supported_classes = (type,)

    def __call__(self, cls: typing.Type):
        component = Component.get_by_cls(cls)
        component.annotations.add(self.annotation, unique=self.unique, single=self.single)
        return cls


class annotate_method(annotate_base):
    _supported_classes = (ComponentMethod, types.FunctionType)

    def __call__(self, func_or_method: typing.Union[types.FunctionType, ComponentMethod]):
        method = ComponentMethod.get_or_create(func_or_method)
        method.annotations.add(self.annotation, unique=self.unique, single=self.single)
        return method
