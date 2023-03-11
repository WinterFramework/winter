from abc import ABC
from typing import List

from injector import Module

from winter_messaging_outbox_transacton.middleware_registry import Middleware


class WorkerConfiguration(ABC):
    def get_modules_for_injector(self) -> List[Module]:
        return []

    def get_middlewares(self) -> List[Middleware]:
        return []
