import uuid

from tests.controllers import ControllerWithPathParameters
from tests.controllers import SimpleController
from winter.web.routing import reverse


def test_reverse_without_args():
    url = reverse(SimpleController.hello)

    # Assert
    assert url == '/winter-simple/'


def test_reverse_with_args():
    uid = uuid.uuid4()
    url = reverse(
        ControllerWithPathParameters.test,
        args=('param1', 1, 'one', uid, '1'),
    )
    # Assert
    assert url == f'/controller_with_path_parameters/param1/1/one/{uid}/1/'


def test_reverse_with_kwargs():
    uid = uuid.uuid4()
    url = reverse(
        ControllerWithPathParameters.test,
        kwargs={
            'param1': 'param1',
            'param2': '1',
            'param3': 'one',
            'param4': uid,
            'param5': '1',
        },
    )
    # Assert
    assert url == f'/controller_with_path_parameters/param1/1/one/{uid}/1/'
