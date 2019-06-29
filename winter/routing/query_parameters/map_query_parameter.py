from .map_query_parameter_annotation import MapQueryParameterAnnotation
from ...core import annotate_method


def map_query_parameter(name: str, *, to: str):
    annotation = MapQueryParameterAnnotation(name, to)
    return annotate_method(annotation, unique=True)
