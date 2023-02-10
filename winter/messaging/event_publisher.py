from abc import ABC
from abc import abstractmethod

from .event import Event


class EventPublisher(ABC):
    @abstractmethod
    def emit(self, event: Event):
        pass
