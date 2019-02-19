import inspect
import typing

if typing.TYPE_CHECKING:
    from .component_method import ComponentMethod


class ComponentMethodArgument:

    def __init__(self, method: ComponentMethod, name, type_):
        self.method = method
        self.name = name
        self.type_ = type_

    @property
    def parameter(self) -> inspect.Parameter:
        return self.method.signature.parameters[self.name]
