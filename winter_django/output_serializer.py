from dataclasses import dataclass
from typing import Dict
from typing import Optional
from typing import Type

from rest_framework.serializers import Serializer

from winter.core import ComponentMethod
from winter.core import annotate
from winter.web.output_processor import register_output_processor
from .output_processor import DRFOutputProcessor


@dataclass
class OutputSerializer:
    class_: Type[Serializer]
    kwargs: Dict


_output_serializers = {}


def output_serializer(serializer_class: Type[Serializer], **serializer_kwargs):
    annotation = OutputSerializer(serializer_class, serializer_kwargs)

    def wrapper(method):
        method = annotate(annotation)(method)
        output_processor = DRFOutputProcessor(serializer_class, serializer_kwargs)
        method = register_output_processor(method, output_processor)
        return method

    return wrapper


def get_output_serializer(method: ComponentMethod) -> Optional[OutputSerializer]:
    return method.annotations.get_one_or_none(OutputSerializer)
