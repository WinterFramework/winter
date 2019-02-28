from enum import Enum
from typing import Type

from .type_inspection import inspect_enum


def inspect_enum_class(enum_class: Type[Enum]) -> dict:
    type_info = inspect_enum(enum_class)
    return type_info.as_dict()
