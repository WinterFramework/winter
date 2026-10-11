"""Deprecated since 33.0, removed in 34.0. Use winter.django."""
from winter._deprecation import alias_modules
from winter._deprecation import deprecated_package

deprecated_package('winter_django', 'winter.django')
alias_modules(prefixes={'winter_django': 'winter.django'})

from winter.django import *  # noqa: E402, F401, F403
