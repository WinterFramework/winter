import pytest

from winter.web.exceptions import RequestDataDecodeException
from winter.web.pagination import order_by


def test_with_default_not_in_allowed_fields():
    with pytest.raises(RequestDataDecodeException) as exception:
        order_by(['id'], default_sort=('uid',))

    assert exception.value.args == ('Failed to decode request data',)
    assert exception.value.errors == {'error': 'Fields do not allowed as order by fields: "uid"'}
