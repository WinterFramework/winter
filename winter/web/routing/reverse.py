from types import MappingProxyType

from django import urls

from winter.core import ComponentMethod


def reverse(method: ComponentMethod, args=(), kwargs=MappingProxyType({})):
    return urls.reverse(method.full_name, args=args, kwargs=kwargs)
