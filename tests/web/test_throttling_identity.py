from unittest import mock

from winter.web.throttling import get_throttling_identity
from winter.web.throttling import identity
from winter.web.throttling import remote_address_identity


def _request(headers=None, remote_address='10.0.0.1'):
    request = mock.Mock()
    request.headers = headers or {}
    request.remote_address = remote_address
    return request


def test_remote_address_identity_uses_the_socket_address():
    assert remote_address_identity(_request()) == '10.0.0.1'


def test_remote_address_identity_prefers_x_forwarded_for():
    request = _request(headers={'X-Forwarded-For': '203.0.113.5, 10.0.0.1'})

    assert remote_address_identity(request) == '203.0.113.5,10.0.0.1'


def test_installed_resolver_decides_the_identity():
    with mock.patch.object(identity, '_identity_resolver', lambda request: 'api-key'):
        assert get_throttling_identity(_request()) == 'api-key'
