from enum import Enum
from typing import Collection

from pydantic.dataclasses import dataclass


class Sort:

    @dataclass
    class Order:

        class Direction(Enum):
            ASC = 'ASC'
            DESC = 'DESC'

        direction: Direction = Direction.ASC
        field: str

    def __init__(self, *orders: Order):
        self._orders = list(orders)

    @property
    def orders(self) -> Collection[Order]:
        return tuple(self._orders)

    @staticmethod
    def by(*fields: str) -> 'Sort':
        if len(fields) == 0:
            raise ValueError('Specify at least one field.')

        orders = (Sort.Order(field=field) for field in fields)
        return Sort(*orders)

    def and_(self, sort: 'Sort') -> 'Sort':
        self._orders.extend(sort.orders)
        return self

    def asc(self):
        self._set_direction(Sort.Order.Direction.ASC)

    def desc(self):
        self._set_direction(Sort.Order.Direction.DESC)

    def _set_direction(self, direction: Order.Direction):
        for order in self._orders:
            order.direction = direction
