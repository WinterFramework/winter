import pytest

import winter
from winter.web.routing import get_route
from winter_openapi.generator import determine_path_prefix
from winter_openapi.generator import get_url_path_tag
from winter_openapi.generator import get_url_path_without_prefix


def test_determine_path_prefix_when_prefix_exist():
    class _TestAPI:
        @winter.route_get('prefix-1/prefix-2/get-resource')
        def get_resource(self):  # pragma: no cover
            pass

        @winter.route_post('prefix-1/prefix-3/post-resource')
        def post_resource(self):  # pragma: no cover
            pass


    route_1 = get_route(_TestAPI.get_resource)
    route_2 = get_route(_TestAPI.post_resource)

    # Act
    path_prefix = determine_path_prefix([route_1, route_2])

    # Assert
    assert path_prefix == '/prefix-1'


def test_determine_path_prefix_without_prefix():
    class _TestAPI:
        @winter.route_get('get-resource')
        def get_resource(self):  # pragma: no cover
            pass

        @winter.route_post('post-resource')
        def post_resource(self):  # pragma: no cover
            pass


    route_1 = get_route(_TestAPI.get_resource)
    route_2 = get_route(_TestAPI.post_resource)

    # Act
    path_prefix = determine_path_prefix([route_1, route_2])

    # Assert
    assert path_prefix == '/'


def test_determine_path_prefix_with_no_path():
    class _TestAPI:
        @winter.route_get()
        def get_resource(self):  # pragma: no cover
            pass

        @winter.route_post()
        def post_resource(self):  # pragma: no cover
            pass


    route_1 = get_route(_TestAPI.get_resource)
    route_2 = get_route(_TestAPI.post_resource)

    # Act
    path_prefix = determine_path_prefix([route_1, route_2])

    # Assert
    assert path_prefix == '/'


def test_determine_path_prefix_ignore_params():
    class _TestAPI:
        @winter.route_get('{id}/get-resource')
        def get_resource(self):  # pragma: no cover
            pass

        @winter.route_post('{id}/post-resource')
        def post_resource(self):  # pragma: no cover
            pass


    route_1 = get_route(_TestAPI.get_resource)
    route_2 = get_route(_TestAPI.post_resource)

    # Act
    path_prefix = determine_path_prefix([route_1, route_2])

    # Assert
    assert path_prefix == '/'


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
    assert url_path_tag == ''


def test_get_url_path_tag_when_url_path_is_prefix():
    class _TestAPI:
        @winter.route_get('prefix')
        def get_resource(self):  # pragma: no cover
            pass

    route = get_route(_TestAPI.get_resource)

    # Act
    url_path_tag = get_url_path_tag(route, '/prefix')

    # Assert
    assert url_path_tag == ''


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
