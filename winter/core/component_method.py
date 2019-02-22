import inspect
import types
import typing
from types import FunctionType

from .annotations import Annotations
from .component_method_argument import ComponentMethodArgument

if typing.TYPE_CHECKING:
    from .component import Component


class ComponentMethod:

    def __init__(self, func: typing.Union[FunctionType, 'ComponentMethod']):
        self.func = func
        self.name: str = None
        self.component: 'Component' = None
        self.annotations = Annotations()

        self._component_cls: typing.Type = None
        self._metadata_storage = {}

        type_hints = typing.get_type_hints(func)
        self.return_value_type = type_hints.pop('return', None)
        self._arguments = self._build_arguments(type_hints)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.func.__get__(instance, owner)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __set_name__(self, owner: typing.Type, name: str):
        self._component_cls = owner
        self.name = name

    @property
    def arguments(self) -> typing.Collection[ComponentMethodArgument]:
        return tuple(self._arguments.values())

    def get_argument(self, name: str) -> typing.Optional['ComponentMethodArgument']:
        return self._arguments.get(name)

    @property
    def signature(self) -> inspect.Signature:
        return inspect.signature(self.func)

    def _build_arguments(self, argument_type_hints: dict) -> typing.Mapping:
        arguments = {
            arg_name: ComponentMethodArgument(self, arg_name, arg_type)
            for arg_name, arg_type in argument_type_hints.items()
        }
        return arguments


def component_method(func: typing.Union[types.FunctionType, ComponentMethod]) -> ComponentMethod:
    if isinstance(func, ComponentMethod):
        return func
    return ComponentMethod(func)
