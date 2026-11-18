from abc import ABC
from abc import abstractmethod


class Interceptor(ABC):
    """
    Runs before the API method in each request of the web applications that list it. The arguments of pre_handle are
    resolved like those of an API method: a `Route` argument, for one, gets the route of the request and its method.
    """

    @abstractmethod
    def pre_handle(self, **kwargs):
        pass
