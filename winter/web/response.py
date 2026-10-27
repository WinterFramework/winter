import dataclasses
from typing import Any


@dataclasses.dataclass
class Response:
    """
    What winter.web hands to an adapter after handling a request, and what an API method or
    exception handler returns to bypass JSON encoding.

    `body` is the final payload as bytes, or an object of the native response types of the adapter
    in use (a Django HttpResponse, for example), which the adapter sends as is.
    """
    status_code: int
    body: Any = b''
    headers: dict[str, str] = dataclasses.field(default_factory=dict)
