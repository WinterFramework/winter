import enum
import re
import uuid

import pytest

from winter.core import ComponentMethod
from winter.http.urls import rewrite_uritemplate_with_regexps


class _OneTwoEnum(enum.Enum):
    ONE = 'one'
    TWO = 'two'


@pytest.mark.parametrize(('url_path', 'param_type', 'expected_url_path', 'example_url'), (
    (r'/{param}/', int, r'/(?P<param>\d+)/', r'/1/'),
    (r'/{param}/', str, r'/(?P<param>[^/]+)/', r'/test/'),
    (r'/{param}/', _OneTwoEnum, r'/(?P<param>((one)|(two)))/', r'/one/'),
    (
        r'/{param}/',
        uuid.UUID,
        r'/(?P<param>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/',
        fr'/{uuid.uuid4()}/',
    ),
))
def test_rewrite_uritemplate_with_regexps(url_path, param_type, expected_url_path, example_url):
    def method(param: param_type):
        return param

    method = ComponentMethod(method)

    # Act
    rewritten_url_path = rewrite_uritemplate_with_regexps(url_path, [method])

    # Assert
    assert rewritten_url_path == expected_url_path
    assert re.match(rewritten_url_path, example_url)


def test_rewrite_uritemplate_with_regexps_with_different_types_in_methods():
    def method1(param: int):
        return param

    def method2(param: str):
        return param

    method1 = ComponentMethod(method1)
    method2 = ComponentMethod(method2)
    argument_types = {int, str}

    # Act
    with pytest.raises(Exception) as exception:
        rewrite_uritemplate_with_regexps('/{param}/', [method1, method2])

    # Assert
    assert str(exception.value) == (
        f'Different methods are bound to the same path variable, '
        f'but have different types annotated: {argument_types}'
    )
