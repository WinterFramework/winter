import inspect
import typing

import dataclasses
from django.utils.functional import cached_property

from .. import type_utils

if typing.TYPE_CHECKING:  # pragma: no cover
    from .component_method import ComponentMethod


@dataclasses.dataclass(frozen=True)
class ComponentMethodArgument:
    method: 'ComponentMethod'
    name: str
    type_: typing.Type

    @property
    def parameter(self) -> inspect.Parameter:
        return self.method.signature.parameters[self.name]

    def has_default(self) -> bool:
        return self.default is not inspect.Parameter.empty

    @cached_property
    def default(self):
        return self.parameter.default

    @property
    def required(self) -> bool:
        return self.default is inspect.Parameter.empty and not type_utils.is_optional(self.type_)
