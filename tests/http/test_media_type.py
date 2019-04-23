import pytest

from winter.http import InvalidMediaTypeException
from winter.http import MediaType


@pytest.mark.parametrize('media_type, expected_result', [
    ('*', ('*', '*', {})),
    ('*/*', ('*', '*', {})),
    ('abc/*', ('abc', '*', {})),
    ('application/json', ('application', 'json', {})),
    ('application/json; charset=utf-8', ('application', 'json', {'charset': 'utf-8'})),
    ('application/xml; charset=utf-8', ('application', 'xml', {'charset': 'utf-8'})),
    ('application/problem+xml; charset=utf-8; boundary=secondary', ('application', 'problem+xml', {
        'charset': 'utf-8',
        'boundary': 'secondary',
    })),
])
def test_valid_media_types(media_type, expected_result):
    result = MediaType.parse(media_type)
    assert result == expected_result


@pytest.mark.parametrize('media_type, expected_message', [
    ('*/abc', 'Wildcard is allowed only in */* (all media types)'),
    ('*/', 'Empty subtype is specified'),
    ('/', 'Empty type is specified'),
    ('/test', 'Empty type is specified'),
    ('', 'Media type must not be empty'),
    ('test', 'Media type must contain "/"'),
    ('test/test/test', 'Invalid media type format'),
    ('test/test; hz', 'Invalid media type parameter list'),
])
def test_invalid_media_types(media_type, expected_message):
    with pytest.raises(InvalidMediaTypeException) as exception_info:
        MediaType.parse(media_type)

    assert exception_info.value.message == expected_message


@pytest.mark.parametrize(('first', 'second'), (
    ('type/subtype', '  type / subtype  '),
    ('type/subtype;charset=utf-8', '  type / subtype; charset = utf-8  '),
))
def test_comparing_media_types(first, second):
    first_media_type = MediaType(first)
    second_media_type = MediaType(second)

    assert first_media_type == second_media_type
    assert hash(first_media_type) == hash(second_media_type)


def test_comparing_with_other_types():
    assert MediaType.ALL != '*'


@pytest.mark.parametrize('media_type, expected_str', [
    (MediaType(' * '), '*/*'),
    (MediaType(' application/problem+xml; charset=utf-8;  boundary=secondary '),
     'application/problem+xml; charset=utf-8; boundary=secondary'),
])
def test_str_representation(media_type, expected_str):
    assert str(media_type) == expected_str
