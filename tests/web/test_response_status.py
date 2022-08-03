from http import HTTPStatus

import pytest

import winter
from winter.web.default_response_status import get_default_response_status


@pytest.mark.parametrize('as_int', [True, False])
@pytest.mark.parametrize('response_status', HTTPStatus)
def test_response_status(response_status, as_int):
    if as_int:
        response_status = response_status.value

    class TestClass:
        @winter.response_status(response_status)
        def handler(self):  # pragma: no cover
            pass

    status = get_default_response_status('post', TestClass.handler)

    assert status == response_status


def test_response_status_with_invalid_status():
    response_status = 1
    message = f'{response_status} is not a valid HTTPStatus'

    with pytest.raises(ValueError, match=message):
        winter.response_status(response_status)
