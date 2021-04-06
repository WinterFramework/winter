from abc import ABC
from abc import abstractmethod

from .controller import get_instance
from .interceptor import InterceptorRegistry
from .interceptor import interceptor_registry


class Configurer(ABC):
    @abstractmethod
    def add_interceptors(self, registry: InterceptorRegistry):
        pass


def run_configurers():
    for configurer_class in Configurer.__subclasses__():
        configurer = get_instance(configurer_class)
        configurer.add_interceptors(interceptor_registry)
