import uuid

from tests.api import APIWithPathParameters
from tests.api import SimpleAPI
from winter.web.routing import reverse


def test_reverse_without_args():
    url = reverse(SimpleAPI.hello)

    # Assert
    assert url == '/winter-simple/'


def test_reverse_with_args():
    uid = uuid.uuid4()
    url = reverse(
        APIWithPathParameters.test,
        args=('param1', 1, 'one', uid, '1'),
    )
    # Assert
    assert url == f'/with-path-parameters/param1/1/one/{uid}/1/'


def test_reverse_with_kwargs():
    uid = uuid.uuid4()
    url = reverse(
        APIWithPathParameters.test,
        kwargs={
            'param1': 'param1',
            'param2': '1',
            'param3': 'one',
            'param4': uid,
            'param5': '1',
        },
    )
    # Assert
    assert url == f'/with-path-parameters/param1/1/one/{uid}/1/'
