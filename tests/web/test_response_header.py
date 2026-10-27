import datetime
import enum
import uuid
from http import HTTPStatus

import pytest

from winter.web import ResponseHeader


def test_response_header_sets_header():
    headers = {}
    header = ResponseHeader[str](headers, 'My-Header')

    # Act
    header.set('value')

    assert headers == {'my-header': 'value'}


@pytest.mark.parametrize('value_type, name', [
    (uuid.UUID, 'UUID'),
    (bool, 'bool'),
    (datetime.date, 'date'),
    (list[int], 'list[int]'),
])
def test_response_header_of_type_without_header_format_is_rejected(value_type, name):
    # Act
    with pytest.raises(TypeError) as exception_info:
        ResponseHeader[value_type]

    # Assert
    assert str(exception_info.value) == f'ResponseHeader[{name}]: a response header is str, int or datetime'


@pytest.mark.parametrize('value, message', [
    ('30', "retry-after: '30' is not int"),
    (True, 'retry-after: True is not int'),
])
def test_response_header_rejects_value_of_other_type(value, message):
    header = ResponseHeader[int]({}, 'Retry-After')

    # Act
    with pytest.raises(TypeError) as exception_info:
        header.set(value)

    # Assert
    assert str(exception_info.value) == message


class _Status(enum.StrEnum):
    ACTIVE = 'active'


def test_response_header_rejects_enum():
    header = ResponseHeader[str]({}, 'X-Status')

    # Act
    with pytest.raises(TypeError) as exception_info:
        header.set(_Status.ACTIVE)

    # Assert
    assert str(exception_info.value) == "x-status: an enum is set by its value, not <_Status.ACTIVE: 'active'>"


def test_response_header_rejects_datetime_without_time_zone():
    header = ResponseHeader[datetime.datetime]({}, 'Last-Modified')

    # Act
    with pytest.raises(ValueError) as exception_info:
        header.set(datetime.datetime(2026, 10, 27, 9, 54))

    # Assert
    assert str(exception_info.value) == (
        'last-modified: a datetime without a time zone has no HTTP-date, give it tzinfo'
    )


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


def test_datetime_response_header_is_http_date_in_gmt(api_client):
    # Act
    response = api_client.get('/with-response-headers/datetime-header/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'OK'
    assert response.headers['x-header'] == 'Tue, 27 Oct 2026 09:54:30 GMT'


def test_two_response_headers(api_client):
    # Act
    response = api_client.get('/with-response-headers/two-headers/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == 'OK'
    assert response.headers['x-header1'] == 'header1'
    assert response.headers['x-header2'] == 'header2'
