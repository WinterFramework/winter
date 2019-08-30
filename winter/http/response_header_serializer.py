import abc
from abc import abstractmethod
from typing import List
from typing import Optional
from typing import Type


class ResponseHeaderSerializer(abc.ABC):
    """ResponseHeaderSerializer interface is used to convert different response header values to string."""

    @abstractmethod
    def is_supported(self, header_name: str, value_type: Optional[Type] = None) -> bool:  # pragma: no cover
        pass

    @abstractmethod
    def serialize(self, value, header_name: str) -> str:  # pragma: no cover
        pass


class ResponseHeadersSerializer:
    def __init__(self):
        self._serializers: List[ResponseHeaderSerializer] = []

    def add_serializer(self, serializer: ResponseHeaderSerializer):
        self._serializers.append(serializer)

    def serialize(self, value, header_name: str) -> str:
        serializer = self._get_serializer(header_name)
        if serializer is not None:
            return serializer.serialize(value, header_name)

        serializer = self._get_serializer(header_name, type(value))
        if serializer is not None:
            return serializer.serialize(value, header_name)

        return str(value)

    def _get_serializer(
        self,
        header_name: str,
        value_type: Optional[Type] = None,
    ) -> Optional[ResponseHeaderSerializer]:
        for serializer in self._serializers:
            if serializer.is_supported(header_name, value_type):
                return serializer
        return None


response_headers_serializer = ResponseHeadersSerializer()
