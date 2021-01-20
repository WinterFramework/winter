import abc

from .interceptor_registry import InterceptorRegistry


class Configurer(abc.ABC):
    @abc.abstractmethod
    def add_interceptors(self, registry: InterceptorRegistry):
        pass
