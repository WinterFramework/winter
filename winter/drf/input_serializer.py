from typing import Dict
from typing import Optional
from typing import Type

from dataclasses import dataclass
from rest_framework.serializers import Serializer

_input_serializers = {}


@dataclass
class InputSerializer:
    class_: Type[Serializer]
    kwargs: Dict
    destination_argument_name: str


def input_serializer(serializer_class: Type[Serializer], argument_name: str, **serializer_kwargs):
    def wrapper(func):
        _register_input_serializer(func, argument_name, serializer_class, serializer_kwargs)
        return func
    return wrapper


def get_input_serializer(func) -> Optional[InputSerializer]:
    return _input_serializers.get(func)


def _register_input_serializer(func, argument_name: str, serializer_class: Type[Serializer], serializer_kwargs: Dict):
    assert func not in _input_serializers, f'{func} already has a registered input_serializer'
    _input_serializers[func] = InputSerializer(serializer_class, serializer_kwargs, argument_name)
