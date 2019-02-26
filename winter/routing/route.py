from typing import Tuple

import dataclasses
import uritemplate

from ..core import ComponentMethod
from ..http import MediaType


@dataclasses.dataclass(frozen=True)
class Route:
    http_method: str
    url_path: str
    method: ComponentMethod
    produces: Tuple[MediaType] = None
    consumes: Tuple[MediaType] = None

    @property
    def path_variables(self):
        return uritemplate.variables(self.url_path)
