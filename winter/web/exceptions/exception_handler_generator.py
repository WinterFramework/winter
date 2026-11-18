from abc import ABC
from abc import abstractmethod
from typing import Type

from .problem_handling_info import ProblemHandlingInfo


class ExceptionHandlerGenerator(ABC):
    @abstractmethod
    def generate(self, exception_class: Type[Exception], handling_info: ProblemHandlingInfo) -> Type:
        """A class with an @exception_handler method that handles the exception class."""
