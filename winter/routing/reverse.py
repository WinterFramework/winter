from types import MappingProxyType

from django import urls

from winter.core import ComponentMethod


def reverse(method: ComponentMethod, args=(), kwargs=MappingProxyType({})):
    name = method.get_full_name()

    return urls.reverse(name, args=args, kwargs=kwargs)
