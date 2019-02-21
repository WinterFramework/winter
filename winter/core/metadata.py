import typing

if typing.TYPE_CHECKING:
    from .metadata_item import MetadataItem


class Metadata:

    def __init__(self):
        self.name = None
        self.owner = None

    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        metadata_ = instance.__dict__.get(self.name)
        if metadata_ is not None:
            return metadata_
        metadata_ = instance.__dict__[self.name] = _Metadata()
        return metadata_

    def __str__(self):
        return f'{self.__class__.__name__}({self.owner.__name__} at {self.name})'


class _Metadata:

    def __init__(self):
        self._metadata_storage = {}

    def add(self, metadata_item: 'MetadataItem'):
        metadata_item.set_value(self._metadata_storage)

    def get(self, metadata_item: typing.Union['MetadataItem', typing.Type['MetadataItem']]):
        return self._metadata_storage.get(metadata_item.key)

    def __repr__(self):
        return f'Metadata({self._metadata_storage!r}'
