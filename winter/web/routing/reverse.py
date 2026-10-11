"""Deprecated since 33.0, removed in 34.0. URL reversing depends on the adapter: use winter.django.reverse."""
import warnings
from types import MappingProxyType

from winter.components import ComponentMethod


def reverse(method: ComponentMethod, args=(), kwargs=MappingProxyType({})):
    message = 'winter.web.routing.reverse is deprecated, use winter.django.reverse'
    warnings.warn(message, DeprecationWarning, stacklevel=2)
    from winter.django.reverse import reverse as django_reverse
    return django_reverse(method, args=args, kwargs=kwargs)
