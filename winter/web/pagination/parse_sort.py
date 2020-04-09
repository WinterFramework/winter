import typing

from winter.data.pagination import Sort
from .parse_order import parse_order


def parse_sort(str_sort: typing.Optional[str]) -> typing.Optional[Sort]:
    if not str_sort:
        return None
    sort_parts = str_sort.split(',')
    orders = (parse_order(sort_part) for sort_part in sort_parts)
    return Sort(*orders)
