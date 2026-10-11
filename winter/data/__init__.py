"""Deprecated since 33.0, removed in 34.0. Repositories live in winter.ddd, pagination in winter.pagination."""
from winter._deprecation import alias_modules
from winter._deprecation import deprecated_package

deprecated_package('winter.data', 'winter.ddd and winter.pagination')
alias_modules(
    exact={
        'winter.data.repository': 'winter.ddd.repository',
        'winter.data.exceptions': 'winter.ddd.exceptions',
    },
    prefixes={'winter.data.pagination': 'winter.pagination'},
)

from winter.ddd import CRUDRepository  # noqa: E402
