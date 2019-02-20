import gc
import typing

import winter.core
from winter.core import Component
from winter.core import Metadata
from winter.core import component_method
from winter.core import metadata
from winter.core import is_component
from winter.core import WinterApplication


def test_is_component():
    winter_app = WinterApplication()

    class SimpleComponent:
        pass

    winter_app.add_component(SimpleComponent)
    assert is_component(SimpleComponent)


def test_autodiscover():
    gc.collect()

    @winter.core.component
    class SimpleComponent:
        pass

    winter_app = WinterApplication()

    winter_app.autodiscover()

    assert list(winter_app.components) == [SimpleComponent]


def test_methods():
    class SimpleComponent:

        @component_method
        def simple_method(self):
            return component

    controller = Component(SimpleComponent)

    assert len(controller.methods) == 1, SimpleComponent.simple_method
    method = controller.methods[0]

    assert method is SimpleComponent.simple_method
    component = SimpleComponent()
    assert SimpleComponent.simple_method(component) is component


def test_method_state():

    class PathMetadata(Metadata, key='path'):

        def set_value(self, metadata_storage: typing.Dict):
            metadata_storage[self.key] = self.value

    def route(param: str):
        return metadata(PathMetadata(param))

    class SimpleComponent:

        @route('/url/')
        def simple_method(self):
            return 123

    assert SimpleComponent.simple_method.get_metadata(PathMetadata) == '/url/'
    assert SimpleComponent().simple_method(123)


def test_method_state_many():

    class QueryMetadata(Metadata, key='query'):

        def set_value(self, metadata_storage: typing.Dict):
            queries = metadata_storage.setdefault(self.key, set())
            queries.add(self.value)

    def query_param(param_: str):
        return metadata(QueryMetadata(param_))

    class SimpleComponent:

        @query_param('first')
        @query_param('second')
        def simple_method(self):
            return None

    param = SimpleComponent.simple_method.get_metadata(QueryMetadata)
    assert param == {'second', 'first'}
