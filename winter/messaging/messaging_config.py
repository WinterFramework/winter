from dataclasses import dataclass
from typing import Dict
from typing import Set
from typing import Set


@dataclass
class MessagingConfig:
    topics: Set[str]
    consumers: Dict[str, Set[str]]
