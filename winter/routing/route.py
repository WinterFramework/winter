from typing import Tuple
from typing import Type

import dataclasses

from ..controller import ControllerMethod
from ..http import MediaType


@dataclasses.dataclass(frozen=True)
class Route:
    http_method: str
    url_path: str
    controller_class: Type
    controller_method: ControllerMethod
    produces: Tuple[MediaType] = None
    consumes: Tuple[MediaType] = None
