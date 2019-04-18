from typing import Optional
from typing import Type

from rest_framework import serializers
from rest_framework.request import Request as DRFRequest

from .page import Page
from .utils import get_next_page_url
from .utils import get_previous_page_url


class _MetaSerializer(serializers.Serializer):
    total_count = serializers.IntegerField()
    limit = serializers.IntegerField(source='position.limit', allow_null=True)
    offset = serializers.IntegerField(source='position.offset', allow_null=True)
    previous = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()

    def get_previous(self, page: Page) -> Optional[str]:
        return get_previous_page_url(page, self.request)

    def get_next(self, page: Page) -> Optional[str]:
        return get_next_page_url(page, self.request)

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
            'objects': serializers.ListField(child=child_serializer(), source='items'),
        }
        return type(f'SpecificSerializerFor{child_serializer}', (_PageBaseSerializer,), payloads)


PageSerializer = _PageSerializerFactory()
