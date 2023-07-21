from http import HTTPStatus


def test_api_with_output_template(api_client):
    response = api_client.get('/with-output-template/?name=John', headers={'Test-Authorize': 'user'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == b'Hello, John!'
