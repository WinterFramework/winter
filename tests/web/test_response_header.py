import datetime
import uuid
from http import HTTPStatus

import pytz

from winter.web import ResponseHeader


def test_response_header_sets_header():
    headers = {}
    header = ResponseHeader[uuid.UUID](headers, 'My-Header')
    uid = uuid.uuid4()

    # Act
    header.set(uid)

    assert headers['my-header'] == uid


def test_str_response_header(api_client):
    # Act
    response = api_client.get('/with-response-headers/str-header/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'OK'
    assert response.headers['x-header'] == 'test header'


def test_int_response_header(api_client):
    # Act
    response = api_client.get('/with-response-headers/int-header/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'OK'
    assert response.headers['x-header'] == '123'


def test_datetime_isoformat_response_header(api_client):
    now = datetime.datetime.now()

    # Act
    response = api_client.get(f'/with-response-headers/datetime-isoformat-header/?now={now.timestamp()}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'OK'
    assert response.headers['x-header'] == now.isoformat()


def test_last_modified_response_header(api_client):
    now = datetime.datetime.now()

    # Act
    response = api_client.get(f'/with-response-headers/last-modified-header/?now={now.timestamp()}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'OK'
    assert response.headers['last-modified'] == now.astimezone(pytz.utc).strftime('%a, %d %b %Y %X GMT')


def test_uuid_response_header(api_client):
    uid = uuid.uuid4()

    # Act
    response = api_client.get(f'/with-response-headers/uuid-header/?uid={uid}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'OK'
    assert response.headers['x-header'] == str(uid)


def test_two_response_headers(api_client):
    # Act
    response = api_client.get('/with-response-headers/two-headers/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'OK'
    assert response.headers['x-header1'] == 'header1'
    assert response.headers['x-header2'] == 'header2'


def test_header_without_annotation(api_client):
    # Act
    response = api_client.get('/with-response-headers/header-without-annotation/')

    # Assert
    assert response.status_code == 500  # It's better to be replaced with something more human readable
