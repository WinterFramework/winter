from typing import Optional
from typing import Type

from rest_framework import serializers
from rest_framework.request import Request as DRFRequest
from rest_framework.utils.urls import remove_query_param
from rest_framework.utils.urls import replace_query_param

from .page import Page


class _MetaSerializer(serializers.Serializer):
    total_count = serializers.IntegerField()
    limit = serializers.IntegerField(source='position.limit', allow_null=True)
    offset = serializers.IntegerField(source='position.offset', allow_null=True)
    previous = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()

    def get_previous(self, page: Page) -> Optional[str]:
        offset = page.position.offset or 0
        limit = page.position.limit

        if offset <= 0 or limit is None:
            return None

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, 'limit', limit)

        if offset - limit <= 0:
            return remove_query_param(url, 'offset')

        offset = offset - limit
        return replace_query_param(url, 'offset', offset)

    def get_next(self, page: Page) -> Optional[str]:
        offset = page.position.offset or 0
        limit = page.position.limit
        total = page.total_count

        if page.position.limit is None:
            return None

        if offset + limit >= total:
            return None

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, 'limit', limit)

        return replace_query_param(url, 'offset', offset + limit)

    @property
    def request(self) -> DRFRequest:
        return self.context['request']


class _PageBaseSerializer(serializers.Serializer):
    meta = _MetaSerializer(source='*')


class _PageSerializerFactory:
    def __getitem__(self, child_serializer: Type[serializers.Serializer]) -> Type:
        assert issubclass(child_serializer, serializers.Field), \
            'child_serializer should be inherited from serializers.Field'

        payloads = {
            'objects': serializers.ListField(child=child_serializer(), source='items')
        }
        return type(f'SpecificSerializerFor{child_serializer}', (_PageBaseSerializer,), payloads)


PageSerializer = _PageSerializerFactory()
