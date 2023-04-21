from abc import ABC
from abc import abstractmethod


class MessagingApp(ABC):
    @abstractmethod
    def setup(self, injector):
        pass
