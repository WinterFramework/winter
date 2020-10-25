import abc
from typing import Any

from rest_framework.request import Request


class ExceptionMapper(abc.ABC):
    @abc.abstractmethod
    def to_response_body(self, request: Request, exception: Exception) -> Any:
        pass
