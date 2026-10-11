from winter._deprecation import alias_modules

alias_modules(prefixes={'winter.data.pagination': 'winter.pagination'})

from .repository import CRUDRepository  # noqa: E402
