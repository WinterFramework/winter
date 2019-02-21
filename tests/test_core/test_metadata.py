import typing

from winter.core import Component
from winter.core import MetadataItem
from winter.core import is_component
from winter.core import metadata


class PathMetadata(MetadataItem, key='path'):

    def set_value(self, metadata_storage: typing.Dict):
        metadata_storage[self.key] = self.value


def route(path: str):
    return metadata(PathMetadata(path))


def test_on_class():

    @route('test')
    class SimpleComponent:
        pass

    assert is_component(SimpleComponent)
    component = Component.get_by_cls(SimpleComponent)
    assert component.metadata.get(PathMetadata) == 'test'


def test_on_method():

    class SimpleComponent:

        @route('test')
        def method(self):
            pass

    assert SimpleComponent.method.metadata.get(PathMetadata) == 'test'