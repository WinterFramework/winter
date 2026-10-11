"""Deprecated since 33.0, removed in 34.0. Use winter.sqlalchemy."""
from winter._deprecation import alias_modules
from winter._deprecation import deprecated_package

deprecated_package('winter_sqlalchemy', 'winter.sqlalchemy')
alias_modules(prefixes={'winter_sqlalchemy': 'winter.sqlalchemy'})

from winter.sqlalchemy import *  # noqa: E402, F401, F403
