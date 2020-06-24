from winter.core import annotate_method
from .map_query_parameter_annotation import MapQueryParameterAnnotation


def map_query_parameter(name: str, *, to: str):
    annotation = MapQueryParameterAnnotation(name, to)
    return annotate_method(annotation, unique=True)
