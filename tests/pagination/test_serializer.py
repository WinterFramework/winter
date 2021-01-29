import dataclasses

import pytest
from mock import Mock
from rest_framework import serializers

from winter.data.pagination import Page
from winter.data.pagination import PagePosition
from winter_django import PageSerializer


@dataclasses.dataclass
class _TestEntity:
    number: int


class _TestSerializer(serializers.Serializer):
    number = serializers.IntegerField()


class _TestSerializerWithMeta(serializers.Serializer):
    number = serializers.IntegerField()

    class Meta:
        ref_name = 'SomeRefNameForTestSerializer'


@pytest.mark.parametrize(('limit', 'offset', 'expected_previous', 'expected_next'), (
    (1, 1, 'test-url.com?limit=1', 'test-url.com?limit=1&offset=2'),
    (None, None, None, None),
    (2, 3, 'test-url.com?limit=2&offset=1', 'test-url.com?limit=2&offset=5'),
    (9, 3, 'test-url.com?limit=9', None),
))
def test_page_serializer(limit, offset, expected_previous, expected_next):
    TestPageSerializer = PageSerializer[_TestSerializer]
    request = Mock()
    request.build_absolute_uri.return_value = 'test-url.com'
    page = Page(
        total_count=10,
        items=[_TestEntity(1)],
        position=PagePosition(limit, offset),
    )
    expected_data = {
        'meta': {
            'total_count': 10,
            'limit': limit,
            'offset': offset,
            'previous': expected_previous,
            'next': expected_next,
        },
        'objects': [{'number': 1}],
    }

    # Act
    data = TestPageSerializer(page, context={'request': request}).data

    # Assert
    assert data == expected_data


def test_page_serializer_meta():
    # Act
    TestPageSerializer = PageSerializer[_TestSerializer]
    TestPageSerializerWithMeta = PageSerializer[_TestSerializerWithMeta]

    # Assert
    assert TestPageSerializer.Meta.ref_name == 'SpecificSerializerFor_TestSerializer'
    assert TestPageSerializerWithMeta.Meta.ref_name == 'SomeRefNameForTestSerializer'
