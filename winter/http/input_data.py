import typing

import dataclasses

from winter.core import annotate_method


@dataclasses.dataclass
class InputDataAnnotation:
    input_data_class: typing.Type
    to: str


def input_data(dataclass: typing.Type, to: str):
    annotation = InputDataAnnotation(dataclass, to)
    return annotate_method(annotation)
