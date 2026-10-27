from collections.abc import Callable

from winter.web.request import Request

IdentityResolver = Callable[[Request], str]
"""Maps a request to the string that throttling counts requests for: a user id, an address, an API key."""


def remote_address_identity(request: Request) -> str:
    """The client address: X-Forwarded-For when a proxy sets it, the socket address otherwise."""
    forwarded_for = request.headers.get('X-Forwarded-For')
    return ''.join(forwarded_for.split()) if forwarded_for else request.remote_address
