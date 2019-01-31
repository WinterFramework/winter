from collections import OrderedDict
from enum import Enum
from typing import Type

from drf_yasg import openapi
from drf_yasg.inspectors.field import get_basic_type_info_from_hint


def inspect_enum_class(enum_class: Type[Enum]) -> dict:
    enum_type = openapi.TYPE_STRING
    enum_values = [entry.value for entry in enum_class]
    # Try to infer type based on enum values
    enum_value_types = {type(v) for v in enum_values}
    if len(enum_value_types) == 1:
        values_type = get_basic_type_info_from_hint(next(iter(enum_value_types)))
        if values_type:
            enum_type = values_type.get('type', enum_type)
    return OrderedDict([
        ('type', enum_type),
        ('enum', enum_values),
    ])
