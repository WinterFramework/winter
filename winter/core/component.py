import inspect
import typing

from .annotations import Annotations
from .component_method import ComponentMethod


class Component:
    _components = {}

    def __init__(self, component_cls: typing.Type):
        self.component_cls = component_cls
        self.annotations = Annotations()
        self.methods: typing.Tuple[ComponentMethod] = tuple(
            component_method for component_method in component_cls.__dict__.values()
            if isinstance(component_method, ComponentMethod)
        )
        for method in self.methods:
            method.component = self

    @classmethod
    def register(cls, cls_: typing.Type) -> 'Component':
        if not inspect.isclass(cls_):
            cls._raise_invalid_class(cls_)
        instance = cls._components.get(cls_)
        if instance is None:
            instance = cls._components[cls_] = cls(cls_)
        return instance

    @classmethod
    def get_all(cls) -> typing.Mapping:
        return cls._components

    @classmethod
    def get_by_cls(cls, component_cls):
        if not inspect.isclass(component_cls):
            cls._raise_invalid_class(component_cls)
        component_ = cls._components.get(component_cls)
        if component_ is None:
            component_ = cls.register(component_cls)
        return component_

    @classmethod
    def _raise_invalid_class(cls, cls_):
        raise ValueError(f'Need class. Got: {cls_}')


def is_component(cls: typing.Type) -> bool:
    return cls in Component.get_all()


def component(cls: typing.Type) -> typing.Type:
    if not inspect.isclass(cls):
        raise ValueError(f'Need class. Given: {cls}')
    Component.register(cls)
    return cls
