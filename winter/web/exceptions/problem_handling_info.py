from typing import Optional

from dataclasses import dataclass


@dataclass(frozen=True)
class ProblemHandlingInfo:
    status: int
    title: Optional[str] = None
    detail: Optional[str] = None
    type: Optional[str] = None
