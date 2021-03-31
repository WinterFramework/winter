from typing import Type

from winter.core import Component


def controller(controller_class: Type) -> Type:
    Component.register(controller_class)
    return controller_class


def get_component(class_: Type) -> Component:
    return Component.get_by_cls(class_)
