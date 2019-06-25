import pytest

import winter


def test_with_default_not_in_allowed_fields():
    with pytest.raises(AssertionError) as exception:
        winter.pagination.order_by(['id'], default='uid')

    assert exception.value.args == ('Not all field in default in allowed_fields',)
