import uuid
from http import HTTPStatus

import pytest
from rest_framework.test import APIClient

from tests.entities import AuthorizedUser
from winter.argument_resolver import ArgumentNotSupported
from winter.http import ResponseHeader


def test_response_header_sets_header():
    headers = {}
    header = ResponseHeader[uuid.UUID](headers, 'My-Header')
    uid = uuid.uuid4()

    # Act
    header.set(uid)

    assert headers['my-header'] == uid


def test_str_response_header():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    # Act
    response = client.get('/with-response-headers/str-header/', content_type='application/json')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'OK'
    assert response['x-header'] == 'test header'


def test_int_response_header():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    # Act
    response = client.get('/with-response-headers/int-header/', content_type='application/json')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'OK'
    assert response['x-header'] == '123'


def test_uuid_response_header():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    uid = uuid.uuid4()

    # Act
    response = client.get(f'/with-response-headers/uuid-header/?uid={uid}', content_type='application/json')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'OK'
    assert response['x-header'] == str(uid)


def test_two_response_headers():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    # Act
    response = client.get('/with-response-headers/two-headers/', content_type='application/json')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'OK'
    assert response['x-header1'] == 'header1'
    assert response['x-header2'] == 'header2'


def test_header_without_annotation():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)

    with pytest.raises(ArgumentNotSupported):
        # Act
        client.get('/with-response-headers/header-without-annotation/', content_type='application/json')
