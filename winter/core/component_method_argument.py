import inspect
import typing

import dataclasses

from .utils import cached_property
from .. import type_utils

if typing.TYPE_CHECKING:  # pragma: no cover
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
    type_: typing.Type

    @cached_property
    def parameter(self) -> inspect.Parameter:
        return self.method.signature.parameters[self.name]

    def get_default(self, default=inspect.Parameter.empty) -> typing.Any:
        if self.parameter.default is not inspect.Parameter.empty:
            return self.parameter.default
        if type_utils.is_optional(self.type_):
            return None
        if default is not inspect.Parameter.empty:
            return default
        raise ArgumentDoesNotHaveDefault(self)

    @property
    def description(self):
        return self.method.docstring.get_argument_description(self.name)

    @property
    def required(self) -> bool:
        return self.parameter.default is inspect.Parameter.empty and not type_utils.is_optional(self.type_)
