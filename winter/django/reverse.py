from types import MappingProxyType

from django import urls

from winter.components import ComponentMethod


def reverse(method: ComponentMethod, args=(), kwargs=MappingProxyType({})):
    """URL of an API method, as registered by create_django_urls_from_routes."""
    return urls.reverse(method.full_name, args=args, kwargs=kwargs)
