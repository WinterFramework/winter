from rest_framework.test import APIClient

from tests.entities import AuthorizedUser


def test_controller_with_output_template():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    response = client.get('/with-output-template/?name=John')

    assert response.status_code == 200
    assert response.content == b'Hello, John!'
