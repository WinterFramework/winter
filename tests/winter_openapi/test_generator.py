import pytest

import winter
from winter.web.routing import get_route
from winter_openapi.generator import determine_path_prefix
from winter_openapi.generator import get_url_path_tag
from winter_openapi.generator import get_url_path_without_prefix


@pytest.mark.parametrize(
    ('url_paths', 'expected_result'),
    [
        (
            [
                'prefix-1/prefix-2/get-resource',
                'prefix-1/prefix-3/post-resource'
            ],
            '/prefix-1',
        ),
        (
            [
                '/prefix-1/get-resource',
                '/prefix-1/post-resource'
            ],
            '/prefix-1',
        ),
        (
            [
                'get-resource',
                'post-resource'
            ],
            '/',
        ),
        (
            [
                '',
                ''
            ],
            '/',
        ),
        (
            [
                '{id}/get-resource',
                '{id}/post-resource'
            ],
            '/',
        ),
    ],
)
def test_determine_path_prefix_when_prefix_exist(url_paths, expected_result):
    # Act
    path_prefix = determine_path_prefix(url_paths)

    # Assert
    assert path_prefix == expected_result


def test_get_url_path_tag():
    class _TestAPI:
        @winter.route_get('prefix/get-resource')
        def get_resource(self):  # pragma: no cover
            pass

    route = get_route(_TestAPI.get_resource)

    # Act
    url_path_tag = get_url_path_tag(route, '/prefix')

    # Assert
    assert url_path_tag == 'get-resource'


def test_get_url_path_tag_ignore_params():
    class _TestAPI:
        @winter.route_get('prefix/{id}/get-resource')
        def get_resource(self):  # pragma: no cover
            pass

    route = get_route(_TestAPI.get_resource)

    # Act
    url_path_tag = get_url_path_tag(route, '/prefix')

    # Assert
    assert url_path_tag is None


def test_get_url_path_tag_when_url_path_is_prefix():
    class _TestAPI:
        @winter.route_get('prefix')
        def get_resource(self):  # pragma: no cover
            pass

    route = get_route(_TestAPI.get_resource)

    # Act
    url_path_tag = get_url_path_tag(route, '/prefix')

    # Assert
    assert url_path_tag == is None


def test_get_url_path_tag_when_url_path_is_shorter_when_prefix():
    class _TestAPI:
        @winter.route_get('get-resource')
        def get_resource(self):  # pragma: no cover
            pass

    route = get_route(_TestAPI.get_resource)

    # Act & Assert
    with pytest.raises(ValueError, match='Invalid path prefix /prefix-1/prefix-2 for url_path get-resource'):
        get_url_path_tag(route, '/prefix-1/prefix-2')


@pytest.mark.parametrize(
    'url_path,path_prefix,expected_result',
    [
        ('/get-resource', '/', '/get-resource'),
        ('/get-resource', '/prefix-1/prefix-2', '/get-resource'),
        ('/prefix-1/prefix-2/get-resource', '/prefix-1/prefix-2', '/get-resource'),
        ('/prefix-1/prefix-2/get-resource', '/prefix-1', '/prefix-2/get-resource'),
        ('prefix-1/prefix-2/get-resource', '/prefix-1/prefix-2', '/get-resource'),
    ]
)
def test_get_url_path_without_prefix(url_path, path_prefix, expected_result):
    # Act
    url_path_without_prefix = get_url_path_without_prefix(url_path, path_prefix)

    # Assert
    assert url_path_without_prefix == expected_result
