from abc import ABC
from abc import abstractmethod
from typing import Any

from rest_framework.request import Request

from .problem_handling_info import ProblemHandlingInfo


class ExceptionMapper(ABC):
    @abstractmethod
    def to_response_body(self, request: Request, exception: Exception, handling_info: ProblemHandlingInfo) -> Any:
        pass
