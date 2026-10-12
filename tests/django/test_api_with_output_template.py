from http import HTTPStatus


def test_api_with_output_template(api_client):
    response = api_client.get('/with-output-template/?name=John')

    assert response.status_code == HTTPStatus.OK
    assert response.content == b'Hello, John!'
