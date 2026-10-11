"""Deprecated since 33.0, removed in 34.0. Use winter.ddd."""
from winter._deprecation import alias_modules
from winter._deprecation import deprecated_package

deprecated_package('winter_ddd', 'winter.ddd')
alias_modules(prefixes={'winter_ddd': 'winter.ddd'})

from winter.ddd import *  # noqa: E402, F401, F403
