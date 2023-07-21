from http import HTTPStatus
from uuid import uuid4


def test_create_django_urls_from_routes(api_client):
    url = f"/notes/?note_id={uuid4()}"

    get_http_response = api_client.get(url, headers={'Test-Authorize': 'user'})
    post_http_response = api_client.post("/notes/", data=dict(name="Name"), headers={'Test-Authorize': 'user'})
    patch_http_response = api_client.patch(url, data=dict(name="New Name"), headers={'Test-Authorize': 'user'})

    assert get_http_response.status_code == HTTPStatus.OK
    assert post_http_response.status_code == HTTPStatus.OK
    assert patch_http_response.status_code == HTTPStatus.OK
