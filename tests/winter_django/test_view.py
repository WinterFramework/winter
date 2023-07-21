from http import HTTPStatus
from uuid import uuid4

from rest_framework.test import APIClient

from tests.entities import AuthorizedUser


def test_create_django_urls_from_routes():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    url = f"/notes/?note_id={uuid4()}"

    get_http_response = client.get(url)
    post_http_response = client.post("/notes/", data=dict(name="Name"))
    patch_http_response = client.patch(url, data=dict(name="New Name"))

    assert get_http_response.status_code == HTTPStatus.OK
    assert post_http_response.status_code == HTTPStatus.OK
    assert patch_http_response.status_code == HTTPStatus.OK
