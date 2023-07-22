import re

from winter.data.pagination import Order
from winter.data.pagination import SortDirection
from winter.web.exceptions import RequestDataDecodeException

_field_pattern = re.compile(r'(-?)(\w+)')


def parse_order(field: str):
    match = _field_pattern.match(field)

    if match is None:
        raise RequestDataDecodeException(f'Invalid field for order: "{field}"')

    direction, field = match.groups()
    direction = SortDirection.DESC if direction == '-' else SortDirection.ASC
    return Order(field, direction)
