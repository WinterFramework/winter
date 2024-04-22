from abc import ABC
from abc import abstractmethod
from typing import List

from .event import Event


class EventPublisher(ABC):
    @abstractmethod
    def emit(self, event: Event):
        pass

    @abstractmethod
    def emit_many(self, events: List[Event]):
        pass
