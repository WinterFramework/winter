import abc
import inspect
import typing

from .component_method import ComponentMethod


class Component(abc.ABC):

    def __init__(self, component_cls: typing.Type):
        self.__class__.register(component_cls)
        self.component_cls = component_cls
        self.methods: typing.List[ComponentMethod] = [
            component_method for component_method in component_cls.__dict__.values()
            if isinstance(component_method, ComponentMethod)
        ]


def is_component(cls: typing.Type):
    return inspect.isclass(cls) and issubclass(cls, Component)
