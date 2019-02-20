import abc
import inspect
import typing

from .component_method import ComponentMethod


class Component(abc.ABC):

    def __init__(self, component_cls: typing.Type):
        self.__class__.register(component_cls)
        self.component_cls = component_cls
        self.methods: typing.Tuple[ComponentMethod] = tuple(
            component_method for component_method in component_cls.__dict__.values()
            if isinstance(component_method, ComponentMethod)
        )
        for method in self.methods:
            method.component = self

    @classmethod
    def get_all_component_classes(cls) -> typing.Set:
        return cls._abc_registry


def is_component(cls: typing.Type) -> typing.Type:
    return inspect.isclass(cls) and issubclass(cls, Component)


def component(cls: typing.Type) -> typing.Type:
    if not inspect.isclass(cls):
        raise ValueError(f'Need class. Given: {cls}')
    Component.register(cls)
    return cls
