import typing

import dataclasses

from winter.core import ComponentMethod


@dataclasses.dataclass
class OrderByFieldsAnnotation:
    allowed_fields: typing.FrozenSet[str]


def get_allowed_order_by_fields(method: ComponentMethod) -> typing.FrozenSet[str]:
    order_by_annotation = method.annotations.get_one_or_none(OrderByFieldsAnnotation)
    if order_by_annotation is None:
        return frozenset()
    return order_by_annotation.allowed_fields
