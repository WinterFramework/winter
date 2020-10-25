import abc
from typing import Type

from .exception_mapper import ExceptionMapper
from .handlers import ExceptionHandler


class ExceptionHandlerGenerator(abc.ABC):
    @abc.abstractmethod
    def generate(self, exception_class: Type[Exception], exception_mapper: ExceptionMapper) -> Type[ExceptionHandler]:
        pass
