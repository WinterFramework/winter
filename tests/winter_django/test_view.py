from tests.controllers.controller_with_path_parameters import ControllerWithPathParameters
from winter_django import create_django_urls


def test_create_django_urls():
    expected_url_pattern = (
        '^controller_with_path_parameters/(?P<param1>[^/]+)/(?P<param2>\\d+)/'
        '(?P<param3>((one)|(two)))/(?P<param4>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/'
        '(?P<param5>((1)|(2)))/$'
    )

    urls = create_django_urls(ControllerWithPathParameters)

    assert len(urls) == 1
    assert urls[0].pattern.regex.pattern == expected_url_pattern
