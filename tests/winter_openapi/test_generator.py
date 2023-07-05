import pytest

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


@pytest.mark.parametrize(
    'url_path, path_prefix, expected_result',
    [
        ('prefix/get-resource', '/prefix', 'get-resource'),
        ('prefix/{id}/get-resource', '/prefix', None),
        ('prefix', '/prefix', None),
    ]
)
def test_get_url_path_tag(url_path, path_prefix, expected_result):
    # Act
    url_path_tag = get_url_path_tag(url_path, path_prefix)

    # Assert
    assert url_path_tag == expected_result


def test_get_url_path_tag_when_url_path_is_shorter_when_prefix():
    # Act & Assert
    with pytest.raises(ValueError, match='Invalid path prefix /prefix-1/prefix-2 for url_path get-resource'):
        get_url_path_tag('get-resource', '/prefix-1/prefix-2')


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
