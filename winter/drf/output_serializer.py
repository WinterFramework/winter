from typing import Dict
from typing import Optional
from typing import Type

from dataclasses import dataclass
from rest_framework.serializers import Serializer

from .output_processor import DRFOutputProcessor
from ..output_processor import register_output_processor


@dataclass
class OutputSerializer:
    class_: Type[Serializer]
    args: Dict


_output_serializers = {}


def output_serializer(serializer_class: Type[Serializer], **serializer_args):
    def wrapper(func):
        output_processor = DRFOutputProcessor(serializer_class, serializer_args)
        register_output_processor(func, output_processor)
        _register_output_serializer(func, serializer_class, serializer_args)
        return func
    return wrapper


def get_output_serializer(func) -> Optional[OutputSerializer]:
    return _output_serializers.get(func)


def _register_output_serializer(func, serializer_class: Type[Serializer], serializer_args: Dict):
    assert func not in _output_serializers
    _output_serializers[func] = OutputSerializer(serializer_class, serializer_args)
