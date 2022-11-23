from abc import ABC
from abc import abstractmethod

from winter.core import ComponentMethod
from .event import Event


class EventBus(ABC):
    @abstractmethod
    def emit(self, event: Event):
        pass

    @abstractmethod
    def register_handler(self, handler_method: ComponentMethod):
        pass
