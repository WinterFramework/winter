from collections.abc import Callable

from winter.web.request import Request

IdentityResolver = Callable[[Request], str]
"""Maps a request to the string that throttling counts requests for: a user id, an address, an API key."""


def remote_address_identity(request: Request) -> str:
    """The client address: X-Forwarded-For when a proxy sets it, the socket address otherwise."""
    forwarded_for = request.headers.get('X-Forwarded-For')
    return ''.join(forwarded_for.split()) if forwarded_for else request.remote_address


_identity_resolver: IdentityResolver = remote_address_identity


def set_throttling_identity_resolver(resolver: IdentityResolver):
    """Adapters and applications install the resolver that knows their notion of a user."""
    global _identity_resolver
    _identity_resolver = resolver


def get_throttling_identity(request: Request) -> str:
    return _identity_resolver(request)
