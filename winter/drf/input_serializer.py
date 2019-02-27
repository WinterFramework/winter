from typing import Dict
from typing import Optional
from typing import Type

from dataclasses import dataclass
from rest_framework.serializers import Serializer

from ..core import ComponentMethod
from ..core import annotate


@dataclass
class InputSerializer:
    class_: Type[Serializer]
    kwargs: Dict
    destination_argument_name: str


def input_serializer(serializer_class: Type[Serializer], argument_name: str, **serializer_kwargs):
    input_serializer_ = InputSerializer(serializer_class, serializer_kwargs, argument_name)
    return annotate(input_serializer_, single=True)


def get_input_serializer(method: ComponentMethod) -> Optional[InputSerializer]:
    return method.annotations.get_one_or_none(InputSerializer)
