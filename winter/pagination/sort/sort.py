import itertools
from enum import Enum

from dataclasses import dataclass


class SortDirection(Enum):
    ASC = 'ASC'
    DESC = 'DESC'


@dataclass(frozen=True)
class Order:
    field: str
    direction: SortDirection = SortDirection.ASC

    def __str__(self):
        return ('-' if self.direction == SortDirection.DESC else '') + self.field


class Sort:

    def __init__(self, *orders: Order):
        self.orders = orders

    @staticmethod
    def by(*fields: str) -> 'Sort':
        if len(fields) == 0:
            raise ValueError('Specify at least one field.')

        orders = (Order(field=field) for field in fields)
        return Sort(*orders)

    def and_(self, sort: 'Sort') -> 'Sort':
        orders = itertools.chain(self.orders, sort.orders)
        return Sort(*orders)

    def asc(self) -> 'Sort':
        orders = (Order(field=order.field, direction=SortDirection.ASC) for order in self.orders)
        return Sort(*orders)

    def desc(self) -> 'Sort':
        orders = (Order(field=order.field, direction=SortDirection.DESC) for order in self.orders)
        return Sort(*orders)

    def __repr__(self):
        sort_fields = ','.join(map(str, self.orders))
        return f"Sort('{sort_fields}')"

    def __eq__(self, other):
        if not isinstance(other, Sort):
            return False
        return self.orders == other.orders

    def __hash__(self):
        return hash(self.orders)
