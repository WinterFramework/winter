from dataclasses import dataclass

from .problem_handling_info import ProblemHandlingInfo


@dataclass(frozen=True)
class ProblemAnnotation:
    handling_info: ProblemHandlingInfo
