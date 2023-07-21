from http import HTTPStatus


def test_api_with_media_types_routing_returns_200(api_client):
    response = api_client.get(
        '/with-media-types-routing/xml/',
        headers={
            'Accept': 'application/xml',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.content == b'Hello, sir!'
    assert response.headers['content-type'] == 'application/xml'
