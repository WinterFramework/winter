import pytest

from rest_framework.test import APIClient


class User:

    @property
    def is_authenticated(self):
        return True


@pytest.mark.parametrize(['data', 'expected_body'], (
    ({'name': 'Winter'}, 'Hello, Winter!'),
    ({'name': 'Stranger'}, 'Hello, Stranger!'),
    ({}, 'Hello, stranger!'),
))
def test_simple_controller(client, data, expected_body):
    client = APIClient()
    user = User()
    client.force_authenticate(user)
    response = client.get('/winter_simple/', data=data)
    assert response.status_code == 200
    assert response.data == expected_body
