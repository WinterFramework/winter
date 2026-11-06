import pytest
from django.test import RequestFactory
from django.urls import resolve

import winter.django

URLCONF = 'tests.django.prefixed_urls'


def _request(method: str, path: str):
    request = RequestFactory().generic(method, path)
    request.urlconf = URLCONF
    return request


@pytest.mark.parametrize('method', ['GET', 'HEAD'])
def test_route_of_request_carries_prefix(method):
    # Act
    route = winter.django.route_of(_request(method, '/api/v1/orders/5/'))

    # Assert
    assert route.url_path == 'api/v1/orders/{order_id}/'
    assert route.http_method == 'GET'


def test_route_of_request_resolved_by_django_comes_from_its_match():
    request = RequestFactory().get('/api/v1/orders/5/')
    request.resolver_match = resolve('/api/v1/orders/5/', urlconf=URLCONF)

    # Act
    route = winter.django.route_of(request)

    # Assert
    assert route.url_path == 'api/v1/orders/{order_id}/'


@pytest.mark.parametrize('method, path', [
    ('GET', '/unknown/'),
    ('GET', '/health/'),
    ('POST', '/api/v1/orders/5/'),
])
def test_request_that_winter_does_not_serve_has_no_route(method, path):
    # Act
    route = winter.django.route_of(_request(method, path))

    # Assert
    assert route is None
