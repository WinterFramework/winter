import pytest


@pytest.mark.parametrize(
    'hello_world_query, hello_world_header',
    [
        ('', None),
        ('?hello_world', 'Hello, World!'),
    ],
)
def test_interceptor_headers(api_client, hello_world_query, hello_world_header):
    url = f'/winter-simple/get/{hello_world_query}'
    response = api_client.get(url)
    assert response.headers.get('x-method') == 'SimpleAPI.get'
    assert response.headers.get('x-hello-world') == hello_world_header
