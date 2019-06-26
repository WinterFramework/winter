import re

from rest_framework import exceptions

from .sort import Order
from .sort import SortDirection

_field_pattern = re.compile(r'(-?)(\w+)')


def parse_order(field: str):
    match = _field_pattern.match(field)

    if match is None:
        raise exceptions.ParseError(f'Invalid field for order: "{field}"')

    direction, field = match.groups()
    direction = SortDirection.DESC if direction == '-' else SortDirection.ASC
    return Order(field, direction)
