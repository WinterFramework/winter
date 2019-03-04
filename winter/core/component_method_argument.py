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
        return f'{self.argument} does not have default'


@dataclasses.dataclass(frozen=True)
class ComponentMethodArgument:
    method: 'ComponentMethod'
    name: str
    type_: typing.Type

    @cached_property
    def parameter(self) -> inspect.Parameter:
        return self.method.signature.parameters[self.name]

    def has_default(self) -> bool:
        return self.parameter.default is not inspect.Parameter.empty

    @cached_property
    def default(self) -> typing.Any:
        if self.has_default():
            return self.parameter.default
        if not self.required:
            return None
        raise ArgumentDoesNotHaveDefault(self)

    @property
    def description(self):
        return self.method.docstring.get_argument_description(self.name)

    @property
    def required(self) -> bool:
        return self.parameter.default is inspect.Parameter.empty and not type_utils.is_optional(self.type_)
