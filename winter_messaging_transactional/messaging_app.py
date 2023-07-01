from abc import ABC
from abc import abstractmethod

from injector import Injector


class MessagingApp(ABC):
    @abstractmethod
    def setup(self, injector: Injector):
        pass
