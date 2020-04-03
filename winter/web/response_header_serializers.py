import datetime
from typing import Optional
from typing import Type

import pytz

from .response_header_serializer import ResponseHeaderSerializer


class DateTimeResponseHeaderSerializer(ResponseHeaderSerializer):
    def is_supported(self, header_name: str, value_type: Optional[Type] = None) -> bool:
        return value_type == datetime.datetime

    def serialize(self, value, header_name: str) -> str:
        assert isinstance(value, datetime.datetime)
        return value.isoformat()


class LastModifiedResponseHeaderSerializer(ResponseHeaderSerializer):
    HEADER_NAME = 'last-modified'

    def is_supported(self, header_name: str, value_type: Optional[Type] = None) -> bool:
        return header_name == self.HEADER_NAME and (value_type is None or value_type == datetime.datetime)

    def serialize(self, value, header_name: str) -> str:
        assert header_name == self.HEADER_NAME
        assert isinstance(value, datetime.datetime)
        return value.astimezone(pytz.utc).strftime('%a, %d %b %Y %X GMT')
