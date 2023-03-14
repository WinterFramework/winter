import importlib
from abc import ABC
from typing import List

from injector import Module

from winter_messaging_outbox_transacton.middleware_registry import MiddlewareClass


class WorkerConfiguration(ABC):
    def get_modules_for_injector(self) -> List[Module]:
        return []

    def get_middlewares(self) -> List[MiddlewareClass]:
        return []


def get_worker_configuration(package_name: str):
    try:
        worker_module = importlib.import_module(f'{package_name}.worker')
        worker_configuration = getattr(worker_module, 'worker_configuration', None)
        if isinstance(worker_configuration, WorkerConfiguration):
            return worker_configuration

        return None
    except ModuleNotFoundError:
        return None
