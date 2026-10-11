"""Deprecated since 33.0, removed in 34.0. Repositories live in winter.ddd, pagination in winter.pagination."""
from winter._deprecation import alias_modules
from winter._deprecation import deprecated_package

deprecated_package('winter.data', 'winter.ddd and winter.pagination')
alias_modules(
    exact={
        'winter.data.repository': 'winter_ddd.repository',
        'winter.data.exceptions': 'winter_ddd.exceptions',
    },
    prefixes={'winter.data.pagination': 'winter.pagination'},
)

from winter_ddd import CRUDRepository  # noqa: E402
