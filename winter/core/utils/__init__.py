"""Deprecated since 33.0, removed in 34.0. The helpers moved next to the code that uses them."""
from winter._deprecation import deprecated_package

deprecated_package('winter.core.utils', 'winter.components.typing, winter.components.nested_types and winter.web')

from winter.components.nested_types import TypeWrapper  # noqa: E402
from winter.components.nested_types import has_nested_type  # noqa: E402
from winter.web.exceptions.beautify_string import camel_to_human  # noqa: E402
from winter.web.pagination.positive_integer import PositiveInteger  # noqa: E402

__all__ = ['TypeWrapper', 'has_nested_type', 'camel_to_human', 'PositiveInteger']
