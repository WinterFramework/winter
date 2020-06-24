from dataclasses import dataclass
from typing import Any
from typing import Dict


@dataclass
class BodyWithContext:
    body: Any
    context: Dict
