import inspect
import typing

from .component_method import ComponentMethod
from .metadata import Metadata


class Component:
    metadata = Metadata()
    _components = {}

    def __init__(self, component_cls: typing.Type):
        self.component_cls = component_cls
        self.methods: typing.Tuple[ComponentMethod] = tuple(
            component_method for component_method in component_cls.__dict__.values()
            if isinstance(component_method, ComponentMethod)
        )
        for method in self.methods:
            method.component = self

    @classmethod
    def register(cls, cls_: typing.Type) -> 'Component':
        instance = cls._components.get(cls_)
        if instance is None:
            instance = cls._components[cls_] = cls(cls_)
        return instance

    @classmethod
    def get_all(cls) -> typing.Mapping:
        return cls._components

    @classmethod
    def get_by_cls(cls, component_cls):
        component_ = cls._components.get(component_cls)
        if component_ is None:
            component_ = cls(component_cls)
        return component_


def is_component(cls: typing.Type) -> bool:
    return cls in Component.get_all()


def component(cls: typing.Type) -> typing.Type:
    if not inspect.isclass(cls):
        raise ValueError(f'Need class. Given: {cls}')
    Component.register(cls)
    return cls
