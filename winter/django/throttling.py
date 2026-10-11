from winter.web import Request
from winter.web.throttling import remote_address_identity
from .request import DjangoRequest


def django_user_identity(request: Request) -> str:
    """Authenticated Django users are throttled by primary key, everyone else by client address."""
    assert isinstance(request, DjangoRequest), 'django_user_identity works with the Django adapter only'
    user = getattr(request.django_request, 'user', None)
    if user is not None and getattr(user, 'is_authenticated', False):
        identity = getattr(user, 'pk', None)
        return str(identity if identity is not None else user.id)
    return remote_address_identity(request)
