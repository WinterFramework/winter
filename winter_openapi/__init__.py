"""Deprecated since 33.0, removed in 34.0. Use winter.openapi."""
from winter._deprecation import alias_modules
from winter._deprecation import deprecated_package

deprecated_package('winter_openapi', 'winter.openapi')
alias_modules(prefixes={'winter_openapi': 'winter.openapi'})

from winter.openapi import *  # noqa: E402, F401, F403
