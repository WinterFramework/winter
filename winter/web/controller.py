from typing import Callable
from typing import NewType
from typing import Optional
from typing import Type
from typing import TypeVar

from winter.core import Component

_Controller = TypeVar('_Controller')
_ControllerType = Type[_Controller]
ControllerFactory = NewType('ControllerFactory', Callable[[Type], object])
_controller_factory: Optional[ControllerFactory] = None


def controller(controller_class: _ControllerType) -> _ControllerType:
    Component.register(controller_class)
    return controller_class


def set_controller_factory(controller_factory: ControllerFactory) -> None:
    global _controller_factory
    _controller_factory = controller_factory


def build_controller(controller_class: _ControllerType) -> _Controller:
    if _controller_factory is None:
        return controller_class()
    return _controller_factory(controller_class)


def get_component(controller_class: _ControllerType) -> Component:
    return Component.get_by_cls(controller_class)
