import typing

from .check_sort import check_sort
from .order_by_annotation import OrderByAnnotation
from .parse_sort import parse_sort
from ...core.annotation_decorator import annotate_method


def order_by(allowed_fields: typing.Iterable[str], default_sort: typing.Tuple[str] = None):
    allowed_fields = frozenset(allowed_fields)
    if default_sort is not None:
        default_sort = parse_sort(','.join(default_sort))
        check_sort(default_sort, allowed_fields)
    annotation = OrderByAnnotation(allowed_fields, default_sort)
    return annotate_method(annotation, single=True)
