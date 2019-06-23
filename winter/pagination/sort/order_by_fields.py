import typing

from .order_by_fields_annotation import OrderByFieldsAnnotation
from ...core.annotation_decorator import annotate_method


def order_by_fields(allowed_fields: typing.Iterable[str]):
    allowed_fields = frozenset(allowed_fields)
    annotation = OrderByFieldsAnnotation(allowed_fields)
    return annotate_method(annotation, single=True)
