import typing

from .order_by_annotation import OrderByAnnotation
from ...core.annotation_decorator import annotate_method


def order_by(allowed_fields: typing.Iterable[str]):
    allowed_fields = frozenset(allowed_fields)
    annotation = OrderByAnnotation(allowed_fields)
    return annotate_method(annotation, single=True)
