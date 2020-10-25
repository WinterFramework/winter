from dataclasses import dataclass


@dataclass(frozen=True)
class ProblemAnnotation:
    status: int
    title: str
    detail: str
    type: str
    auto_handle: bool
