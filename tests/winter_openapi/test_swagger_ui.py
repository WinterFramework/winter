from rest_framework.test import APIClient
from lxml import etree


def test_swagger_ui():
    client = APIClient()

    response = client.get('/swagger-ui/')

    assert response.status_code == 200
    html_parser = etree.HTMLParser()
    etree.HTML(response.content, html_parser)
    assert not html_parser.error_log


def test_swagger_ui_with_params():
    client = APIClient()

    response = client.get('/swagger-ui-with-params/')

    assert response.status_code == 200
    html_parser = etree.HTMLParser()
    etree.HTML(response.content, html_parser)
    assert not html_parser.error_log
