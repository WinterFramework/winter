import pytest
from rest_framework import exceptions

import winter


def test_with_default_not_in_allowed_fields():
    with pytest.raises(exceptions.ParseError) as exception:
        winter.pagination.order_by(['id'], default_sort=('uid',))

    assert exception.value.args == ('Fields do not allowed as order by fields: "uid"',)
