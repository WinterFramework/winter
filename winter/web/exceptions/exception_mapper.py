import abc
from typing import Any

from rest_framework.request import Request

from .problem_handling_info import ProblemHandlingInfo


class ExceptionMapper(abc.ABC):
    @abc.abstractmethod
    def to_response_body(self, request: Request, exception: Exception, handling_info: ProblemHandlingInfo) -> Any:
        pass
