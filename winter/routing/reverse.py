from types import MappingProxyType

from django.urls import reverse as django_reverse

from winter.core import ComponentMethod


def reverse(method: ComponentMethod, args=(), kwargs=MappingProxyType({})):
    name = method.get_full_name()

    return django_reverse(name, args=args, kwargs=kwargs)
