from abc import ABC
from abc import abstractmethod
from typing import List

from injector import Module

from winter.messaging import MessagingConfig
from winter_messaging_transactional.consumer import MiddlewareClass


class MessagingApp(ABC):
    @abstractmethod
    def get_injector_modules(self) -> List[Module]:
        pass

    @abstractmethod
    def get_listener_middlewares(self) -> List[MiddlewareClass]:
        pass

    @abstractmethod
    def get_configuration(self) -> MessagingConfig:
        pass
