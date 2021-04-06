from abc import ABC
from abc import abstractmethod
from typing import Type

from .handlers import ExceptionHandler
from .problem_handling_info import ProblemHandlingInfo


class ExceptionHandlerGenerator(ABC):
    @abstractmethod
    def generate(self, exception_class: Type[Exception], handling_info: ProblemHandlingInfo) -> Type[ExceptionHandler]:
        pass
