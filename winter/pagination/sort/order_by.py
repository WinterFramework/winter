import typing

from .order_by_annotation import OrderByAnnotation
from ...core.annotation_decorator import annotate_method


def order_by(allowed_fields: typing.Iterable[str], default: typing.Optional[str] = None):
    allowed_fields = frozenset(allowed_fields)
    if default is not None:
        assert all(field in allowed_fields for field in default.split(',')), (
            'Not all field in default in allowed_fields'
        )
    annotation = OrderByAnnotation(allowed_fields, default)
    return annotate_method(annotation, single=True)
