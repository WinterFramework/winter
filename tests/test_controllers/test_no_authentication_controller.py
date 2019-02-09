from rest_framework.test import APIClient


def test_no_authentication_controller():
    client = APIClient()
    response = client.get('/winter_no_auth/')
    assert response.status_code == 200
    assert response.json() == 'Hello, World!'
