from enum import Enum
from typing import Collection

from dataclasses import dataclass


class SortDirection(Enum):
    ASC = 'ASC'
    DESC = 'DESC'


@dataclass
class Order:
    field: str
    direction: SortDirection = SortDirection.ASC


class Sort:

    def __init__(self, *orders: Order):
        self._orders = list(orders)

    @property
    def orders(self) -> Collection[Order]:
        return tuple(self._orders)

    @staticmethod
    def by(*fields: str) -> 'Sort':
        if len(fields) == 0:
            raise ValueError('Specify at least one field.')

        orders = (Order(field=field) for field in fields)
        return Sort(*orders)

    def and_(self, sort: 'Sort') -> 'Sort':
        self._orders.extend(sort.orders)
        return self

    def asc(self) -> 'Sort':
        return self._set_direction(SortDirection.ASC)

    def desc(self) -> 'Sort':
        return self._set_direction(SortDirection.DESC)

    def _set_direction(self, direction: SortDirection) -> 'Sort':
        for order in self._orders:
            order.direction = direction
        return self

    def __repr__(self):
        sort_parts = (('-' if order.direction == SortDirection.DESC else '') + order.field for order in self.orders)
        return ','.join(sort_parts)

    def __eq__(self, other):
        if not isinstance(other, Sort):
            return False
        return self.orders == other.orders

    def __hash__(self):
        return hash(tuple((order.field, order.direction) for order in self.orders))
