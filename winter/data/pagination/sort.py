import enum
import itertools
from typing import Tuple

import dataclasses


class SortDirection(enum.Enum):
    ASC = 'ASC'
    DESC = 'DESC'


@dataclasses.dataclass(frozen=True)
class Order:
    field: str
    direction: SortDirection = SortDirection.ASC

    def __str__(self):
        return ('-' if self.direction == SortDirection.DESC else '') + self.field


@dataclasses.dataclass(frozen=True, init=False, repr=False)
class Sort:
    orders: Tuple[Order]

    def __init__(self, *orders: Order):
        object.__setattr__(self, 'orders', orders)

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

    def __str__(self):
        return ','.join(map(str, self.orders))

    def __repr__(self):
        return f"Sort('{self}')"
