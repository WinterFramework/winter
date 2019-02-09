import pytest
from rest_framework.test import APIClient

from ..entities import AuthorizedUser

url_pattern = '/controller-with-param/{param}/{url}/'


@pytest.mark.parametrize(('param', 'url', 'expected_data'), (
        ('string', 'return_str', {'param': 'string'}),
        (123, 'return_int', {'param': 123}),
))
def test_return_str_and_int(param, url, expected_data):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    response = client.get(url_pattern.format(param=param, url=url))

    assert response.status_code == 200
    assert response.json() == expected_data
