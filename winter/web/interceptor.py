import abc


class Interceptor(abc.ABC):
    @abc.abstractmethod
    def pre_handle(self, **kwargs):
        pass


class InterceptorRegistry:
    def __init__(self):
        self._interceptors = []

    def add_interceptor(self, interceptor: Interceptor):
        self._interceptors.append(interceptor)

    def __iter__(self):
        return iter(self._interceptors)


interceptor_registry = InterceptorRegistry()
