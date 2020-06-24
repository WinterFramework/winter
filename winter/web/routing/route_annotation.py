from typing import Tuple

import dataclasses
from winter.web import MediaType


@dataclasses.dataclass(frozen=True)
class RouteAnnotation:
    url_path: str
    http_method: str = None
    produces: Tuple[MediaType] = None  # It's used for swagger only at the moment, but will be used in routing later
    consumes: Tuple[MediaType] = None  # It's used for swagger only at the moment, but will be used in routing later
