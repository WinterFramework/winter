import inspect
from typing import Any
from typing import TYPE_CHECKING
from typing import Type

import dataclasses

from .utils import cached_property
from .utils.typing import is_optional

if TYPE_CHECKING:  # pragma: no cover
    from .component_method import ComponentMethod


class ArgumentDoesNotHaveDefault(Exception):

    def __init__(self, argument: 'ComponentMethodArgument'):
        self.argument = argument

    def __str__(self):
        return f'{self.argument} does not have get_default'


@dataclasses.dataclass(frozen=True)
class ComponentMethodArgument:
    method: 'ComponentMethod'
    name: str
    type_: Type

    @cached_property
    def parameter(self) -> inspect.Parameter:
        return self.method.signature.parameters[self.name]

    def get_default(self, default=inspect.Parameter.empty) -> Any:
        if self.parameter.default is not inspect.Parameter.empty:
            return self.parameter.default
        if is_optional(self.type_):
            return None
        if default is not inspect.Parameter.empty:
            return default
        raise ArgumentDoesNotHaveDefault(self)

    @property
    def description(self):
        return self.method.docstring.get_argument_description(self.name)

    @property
    def required(self) -> bool:
        return self.parameter.default is inspect.Parameter.empty and not is_optional(self.type_)
