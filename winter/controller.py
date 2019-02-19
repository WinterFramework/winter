import inspect
import typing
from typing import Callable
from typing import List
from typing import NewType
from typing import Optional
from typing import Type

from .routing import get_function_route
from .routing import route_table

ControllerFactory = NewType('ControllerFactory', Callable[[Type], object])
_controller_factory: Optional[ControllerFactory] = None
_controllers = {}
_methods = {}


class ControllerComponent:
    def __init__(self, controller_class, methods: List['ControllerMethod']):
        self.controller_class = controller_class
        self.methods = methods

    @property
    def name(self) -> str:
        return self.controller_class.__name__

    def get_method(self, name: str) -> Optional['ControllerMethod']:
        for method in self.methods:
            if method.name == name:
                return method
        return None

    def __repr__(self):
        return f'ControllerComponent({self.controller_class})'


class ControllerMethod:
    def __init__(self, func, url_path: str, http_method: str):
        self.func = func
        self.url_path = url_path
        self.http_method = http_method
        type_hints = typing.get_type_hints(func)
        self.return_value_type = type_hints.pop('return', None)
        self._arguments = self._build_arguments(type_hints)

    @property
    def name(self) -> str:
        return self.func.__name__

    @property
    def arguments(self) -> List['ControllerMethodArgument']:
        return list(self._arguments.values())

    def get_argument(self, name: str) -> Optional['ControllerMethodArgument']:
        return self._arguments.get(name)

    @property
    def signature(self) -> inspect.Signature:
        return inspect.signature(self.func)

    def _build_arguments(self, argument_type_hints: dict):
        arguments = {
            arg_name: ControllerMethodArgument(self, arg_name, arg_type)
            for arg_name, arg_type in argument_type_hints.items()
        }
        return arguments


class ControllerMethodArgument:
    def __init__(self, method: ControllerMethod, name, type_):
        self.method = method
        self.name = name
        self.type_ = type_

    @property
    def parameter(self) -> inspect.Parameter:
        return self.method.signature.parameters[self.name]


def _register_controller(controller_class):
    assert controller_class not in _controllers, f'{controller_class} is already marked as controller'
    controller_methods = []
    routes = {}
    for member in controller_class.__dict__.values():
        route = get_function_route(member)
        if not route:
            continue
        controller_method = ControllerMethod(member, route.url_path, route.http_method)
        route_table.add_route(route, controller_class, controller_method)
        controller_methods.append(controller_method)
        _methods[member] = controller_method
        routes[route] = member
    controller_component = ControllerComponent(controller_class, controller_methods)
    _controllers[controller_class] = controller_component


def controller(controller_class):
    _register_controller(controller_class)
    return controller_class


def set_controller_factory(controller_factory: ControllerFactory):
    global _controller_factory
    _controller_factory = controller_factory


def build_controller(controller_class: Type) -> object:
    if _controller_factory is None:
        return controller_class()
    return _controller_factory(controller_class)


def get_controller_component(controller_class: Type) -> Optional[ControllerComponent]:
    return _controllers.get(controller_class)


def all_controllers() -> List[ControllerComponent]:
    return list(_controllers.values())
