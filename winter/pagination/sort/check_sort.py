import typing

from rest_framework import exceptions

if typing.TYPE_CHECKING:
    from .sort import Sort


def check_sort(sort: 'Sort', allowed_fields: typing.FrozenSet[str]):
    not_allowed_fields = [
        order.field
        for order in sort.orders
        if order.field not in allowed_fields
    ]
    if not_allowed_fields:
        not_allowed_fields = ','.join(not_allowed_fields)
        raise exceptions.ParseError(f'Fields do not allowed as order by fields: "{not_allowed_fields}"')
