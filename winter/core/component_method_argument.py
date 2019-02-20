import inspect
import typing

import dataclasses

if typing.TYPE_CHECKING:
    from .component_method import ComponentMethod


@dataclasses.dataclass(frozen=True)
class ComponentMethodArgument:
    method: 'ComponentMethod'
    name: str
    type_: typing.Type

    @property
    def parameter(self) -> inspect.Parameter:
        return self.method.signature.parameters[self.name]
