import abc
from typing import Any
from typing import List
from typing import Mapping
from typing import Optional
from typing import Protocol


class MultiValueMapping(Protocol):  # pragma: no cover
    """Query parameters as web frameworks expose them: Django's QueryDict, Starlette's QueryParams."""

    def __contains__(self, name: str) -> bool: ...

    def __getitem__(self, name: str) -> str: ...

    def get(self, name: str, default: Any = None) -> Optional[str]: ...

    def getlist(self, name: str) -> List[str]: ...


class Request(abc.ABC):
    """
    An HTTP request as winter.web sees it. Adapters implement it on top of their framework's request object;
    API methods, argument resolvers, interceptors and exception handlers receive it instead of that object.
    """

    @property
    @abc.abstractmethod
    def method(self) -> str:
        """Upper-case HTTP method, e.g. 'GET'."""

    @property
    @abc.abstractmethod
    def path(self) -> str:
        """Request path without the query string, e.g. '/todos/1/'."""

    @property
    @abc.abstractmethod
    def full_path(self) -> str:
        """Request path with the query string, e.g. '/todos/?limit=10'."""

    @property
    @abc.abstractmethod
    def query_parameters(self) -> MultiValueMapping:
        """Query string parameters; a name may carry several values."""

    @property
    @abc.abstractmethod
    def headers(self) -> Mapping[str, str]:
        """Case-insensitive mapping of request headers."""

    @property
    @abc.abstractmethod
    def path_parameters(self) -> Mapping[str, str]:
        """Raw values of the URL template variables of the matched route."""

    @property
    @abc.abstractmethod
    def body(self) -> bytes:
        """Raw request body."""

    @property
    @abc.abstractmethod
    def remote_address(self) -> Optional[str]:
        """IP address of the client as seen by the server."""
