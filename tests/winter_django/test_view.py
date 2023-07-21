from http import HTTPStatus
from uuid import uuid4


def test_create_django_urls_from_routes(api_client):
    url = f"/notes/?note_id={uuid4()}"

    get_http_response = api_client.get(url)
    post_http_response = api_client.post("/notes/", data=dict(name="Name"))
    patch_http_response = api_client.patch(url, data=dict(name="New Name"))

    assert get_http_response.status_code == HTTPStatus.OK
    assert post_http_response.status_code == HTTPStatus.OK
    assert patch_http_response.status_code == HTTPStatus.OK
