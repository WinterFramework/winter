import pytest
from rest_framework.test import APIClient

from .entities import AuthorizedUser


@pytest.mark.parametrize(
    'hello_world_query, hello_world_header',
    [
        ('', None),
        ('?hello_world', 'Hello, World!'),
    ],
)
def test_hello_world_header(hello_world_query, hello_world_header):
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    url = f'/winter-simple/get/{hello_world_query}'
    response = client.get(url)
    assert response.get('x-hello-world') == hello_world_header
