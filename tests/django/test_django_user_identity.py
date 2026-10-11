import pytest
from django.http import HttpRequest

from winter.django import DjangoRequest
from winter.django.throttling import django_user_identity
from tests.user import User


class _UserWithIdOnly:
    is_authenticated = True
    id = 7


def _request(user=None, remote_address='10.0.0.1') -> DjangoRequest:
    django_request = HttpRequest()
    django_request.META['REMOTE_ADDR'] = remote_address
    if user is not None:
        django_request.user = user
    return DjangoRequest(django_request, {})


@pytest.mark.parametrize('user, expected_identity', [
    (User(pk=42), '42'),
    (_UserWithIdOnly(), '7'),
    (None, '10.0.0.1'),
])
def test_django_user_identity(user, expected_identity):
    assert django_user_identity(_request(user)) == expected_identity


def test_django_user_identity_requires_a_django_request():
    with pytest.raises(AssertionError, match='Django adapter only'):
        django_user_identity(object())
