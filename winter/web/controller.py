from typing import Callable
from typing import NewType
from typing import Optional
from typing import Type
from typing import TypeVar

from winter.core import Component

Factory = NewType('Factory', Callable[[Type], object])
_factory: Optional[Factory] = None
T = TypeVar('T')


def controller(controller_class: Type) -> Type:
    Component.register(controller_class)
    return controller_class


def set_factory(controller_factory: Factory) -> None:
    global _factory
    _factory = controller_factory


def get_instance(class_: Type[T]) -> T:
    if _factory is None:
        return class_()
    return _factory(class_)


def get_component(class_: Type) -> Component:
    return Component.get_by_cls(class_)
