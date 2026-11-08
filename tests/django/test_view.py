from http import HTTPStatus
from uuid import uuid4

import pytest
from django.middleware.csrf import CsrfViewMiddleware
from django.test import RequestFactory
from django.urls.resolvers import RegexPattern
from django.urls.resolvers import URLResolver

import winter.django
import winter.web
from winter.web.autodiscovery import find_routes
from tests.web_application import web_application


def test_create_django_urls_from_routes(api_client):
    url = f"/notes/?note_id={uuid4()}"

    get_http_response = api_client.get(url)
    post_http_response = api_client.post("/notes/", json=dict(name="Name"))
    patch_http_response = api_client.patch(url, json=dict(name="New Name"))

    assert get_http_response.status_code == HTTPStatus.OK
    assert post_http_response.status_code == HTTPStatus.OK
    assert patch_http_response.status_code == HTTPStatus.OK


class _OrderAPI:
    @winter.web.route_get('orders/{order_id}/{?q}')
    def get(self, order_id: int, q: str = '') -> str:
        return f'{order_id}{q}'


def test_urls_are_created_under_prefix():
    urls = winter.django.create_urls(web_application(_OrderAPI), prefix='api/v1/')
    resolver = URLResolver(RegexPattern(r'^/'), urls)
    match = resolver.resolve('/api/v1/orders/5/')

    # Act
    response = match.func(RequestFactory().get('/api/v1/orders/5/?q=x'), **match.kwargs)

    # Assert
    assert response.content == b'"5x"'


def test_route_with_prefix_keeps_query_parameters():
    [route] = find_routes(web_application(_OrderAPI))

    # Act
    prefixed_route = route.with_prefix('api/v1/')

    # Assert
    assert prefixed_route.url_path == 'api/v1/orders/{order_id}/'
    assert [parameter.name for parameter in prefixed_route.get_query_parameters()] == ['q']
    assert prefixed_route.method is route.method
    assert prefixed_route.http_method == 'GET'


@pytest.mark.parametrize('prefix', ['api/v1', '/api/v1/'])
def test_prefix_is_path_like_paths_of_routes(prefix):
    app = web_application(_OrderAPI)

    # Act
    with pytest.raises(ValueError) as exception_info:
        winter.django.create_urls(app, prefix=prefix)

    # Assert
    assert str(exception_info.value) == (
        f"A prefix has no leading slash and ends with a slash, like 'public-api/v1/': {prefix!r}"
    )


class _ItemAPI:
    @winter.web.route_post('items/')
    def create(self):  # pragma: no cover
        pass


def test_django_does_not_check_csrf_of_winter_views():
    [url] = winter.django.create_urls(web_application(_ItemAPI))
    middleware = CsrfViewMiddleware(lambda request: None)

    # Act
    response = middleware.process_view(RequestFactory().post('/items/'), url.callback, (), {})

    # Assert
    assert response is None
