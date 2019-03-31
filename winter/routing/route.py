import typing

import dataclasses
import uritemplate

from ..core import ComponentMethod
from ..core import cached_property
from ..http import MediaType


@dataclasses.dataclass(frozen=True)
class Route:
    http_method: str
    url_path: str
    method: ComponentMethod
    produces: typing.Tuple[MediaType] = None
    consumes: typing.Tuple[MediaType] = None

    @cached_property
    def path_variables(self):
        return uritemplate.variables(self.url_path)
