from typing import Any
from typing import Dict

from dataclasses import dataclass


@dataclass
class BodyWithContext:
    body: Any
    context: Dict
