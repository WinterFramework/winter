from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy.sql import Select

from winter.data.pagination import PagePosition
from winter.data.pagination import Sort
from winter.data.pagination import SortDirection

_sort_direction_map = {
    SortDirection.ASC: asc,
    SortDirection.DESC: desc,
}


def paginate(select: Select, page_position: PagePosition) -> Select:
    if page_position.sort:
        select = sort(select, page_position.sort)
    return select.limit(page_position.limit).offset(page_position.offset)


def sort(select: Select, sort: Sort) -> Select:
    order_by_clauses = [_sort_direction_map[order.direction](order.field) for order in sort.orders]
    return select.order_by(*order_by_clauses)
