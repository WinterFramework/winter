from http import HTTPStatus


def test_raw_response_bypasses_json_encoding(api_client):
    response = api_client.get('/with-response/raw/')

    assert response.status_code == HTTPStatus.ACCEPTED
    assert response.content == b'raw bytes'
    assert response.headers['content-type'] == 'text/plain'


def test_output_processor_may_return_a_response(api_client):
    response = api_client.get('/with-response/processed/')

    assert response.status_code == HTTPStatus.OK
    assert response.content == b'42'
    assert response.headers['content-type'] == 'text/plain'


def test_request_describes_the_http_request(api_client):
    response = api_client.get('/with-response/request-info/?x=1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'method': 'GET',
        'path': '/with-response/request-info/',
        'full_path': '/with-response/request-info/?x=1',
        'remote_address': '127.0.0.1',
        'same_django_request': True,
    }
