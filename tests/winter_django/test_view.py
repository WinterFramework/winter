from http import HTTPStatus
from uuid import uuid4

import pytest
from rest_framework.test import APIClient

import winter
from tests.api.api_with_path_parameters import APIWithPathParameters
from tests.entities import AuthorizedUser
from winter.web.routing import get_route
from winter_django import create_django_urls
from winter_django.view import create_django_urls_from_routes


def test_create_django_urls():
    expected_url_pattern = (
        "^with-path-parameters/(?P<param1>[^/]+)/(?P<param2>\\d+)/"
        "(?P<param3>((one)|(two)))/(?P<param4>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/"
        "(?P<param5>((1)|(2)))/$"
    )

    urls = create_django_urls(APIWithPathParameters)

    assert len(urls) == 1
    assert urls[0].pattern.regex.pattern == expected_url_pattern


def test_create_django_urls_from_routes():
    client = APIClient()
    user = AuthorizedUser()
    client.force_authenticate(user)
    url = f"/notes/?note_id={uuid4()}"

    get_http_response = client.get(url)
    post_http_response = client.post("/notes/", data=dict(name="Name"))
    patch_http_response = client.patch(url, data=dict(name="New Name"))

    assert get_http_response.status_code == HTTPStatus.OK
    assert post_http_response.status_code == HTTPStatus.OK
    assert patch_http_response.status_code == HTTPStatus.OK


def test_create_django_urls_from_routes_with_exception():
    class API1:
        @winter.route_get("no_authentication/")
        def get(self):  # pragma: no cover
            pass

    @winter.web.no_authentication
    class API2:
        @winter.route_patch("no_authentication/")
        def update(self):  # pragma: no cover
            pass

    routes = [get_route(API1.get), get_route(API2.update)]

    with pytest.raises(Exception, match="All url path routes must be either with authentication or without"):
        create_django_urls_from_routes(routes=routes)


def test_create_django_urls_from_routes_with_csrf_exempt_exception():
    class API1:
        @winter.route_get("csrf_exempt/")
        def get(self):  # pragma: no cover
            pass

    class API2:
        @winter.web.csrf_exempt
        @winter.route_patch("csrf_exempt/")
        def update(self):  # pragma: no cover
            pass

    routes = [get_route(API1.get), get_route(API2.update)]

    with pytest.raises(Exception, match="All url path routes must be either with csrf or without"):
        create_django_urls_from_routes(routes=routes)
