from typing import FrozenSet
from typing import Optional

import dataclasses

from winter.data.pagination import Sort


@dataclasses.dataclass
class OrderByAnnotation:
    allowed_fields: FrozenSet[str]
    default_sort: Optional[Sort] = None
