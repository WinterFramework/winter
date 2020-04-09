import pytest
from rest_framework import exceptions

from winter.web.pagination import order_by


def test_with_default_not_in_allowed_fields():
    with pytest.raises(exceptions.ParseError) as exception:
        order_by(['id'], default_sort=('uid',))

    assert exception.value.args == ('Fields do not allowed as order by fields: "uid"',)
