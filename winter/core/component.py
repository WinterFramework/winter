import abc
import typing

from .component_method import ComponentMethod


class Component(abc.ABC):

    def __init__(self, controller_cls: typing.Type):
        self.__class__.register(controller_cls)
        self.controller_cls = controller_cls
        self.methods: typing.List[ComponentMethod] = [
            controller_method for controller_method in controller_cls.__dict__.values()
            if isinstance(controller_method, ComponentMethod)
        ]


def is_component(controller_cls):
    return issubclass(controller_cls, Component)
