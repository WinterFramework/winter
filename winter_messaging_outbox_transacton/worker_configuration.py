from abc import ABC
from abc import abstractmethod
from typing import List

from injector import Module


class WorkerConfiguration(ABC):
    @abstractmethod
    def get_modules_for_injector(self) -> List[Module]:
        pass
