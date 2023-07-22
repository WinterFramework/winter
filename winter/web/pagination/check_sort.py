from typing import FrozenSet
from typing import TYPE_CHECKING

from winter.web.exceptions import RequestDataDecodeException

if TYPE_CHECKING:
    from winter.data.pagination import Sort


def check_sort(sort: 'Sort', allowed_fields: FrozenSet[str]):
    not_allowed_fields = [
        order.field
        for order in sort.orders
        if order.field not in allowed_fields
    ]
    if not_allowed_fields:
        not_allowed_fields = ','.join(not_allowed_fields)
        raise RequestDataDecodeException(f'Fields do not allowed as order by fields: "{not_allowed_fields}"')
