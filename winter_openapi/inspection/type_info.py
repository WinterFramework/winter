from collections import OrderedDict
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import Optional
from typing import Type

from .data_formats import DataFormat
from .data_types import DataTypes


@dataclass
class TypeInfo:
    type_: DataTypes
    hint_class: Type
    format_: Optional[DataFormat] = None
    child: Optional['TypeInfo'] = None
    nullable: bool = False
    can_be_undefined: bool = False
    properties: Dict[str, 'TypeInfo'] = field(default_factory=OrderedDict)
    properties_defaults: Dict[str, object] = field(default_factory=dict)
    enum: Optional[list] = None
    title: str = ''
    description: str = ''
