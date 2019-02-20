import functools

from winter.core import Component
from winter.core import is_component
from winter.core.application import WinterApplication
from winter.core.metadata_key import MetadataKey


def test_is_component():
    winter_app = WinterApplication()

    @winter_app.component
    class SimpleController:
        pass

    assert is_component(SimpleController)


def test_methods():
    winter_app = WinterApplication()

    @winter_app.component
    class SimpleComponent:

        @winter_app.component_method
        def simple_method(self):
            return None

    controller = Component(SimpleComponent)

    assert len(controller.methods) == 1, SimpleComponent.simple_method
    method = controller.methods[0]

    assert method is SimpleComponent.simple_method


def test_method_state():
    winter_app = WinterApplication()

    def route(param: str):
        metadata_key = MetadataKey('path')
        state_value = param
        return functools.partial(winter_app.component_method, metadata_key=metadata_key, state_value=state_value)

    @winter_app.component
    class SimpleComponent:

        @route('/url/')
        def simple_method(self):
            return None

    metadata_key = MetadataKey('path')
    assert SimpleComponent.simple_method.get_metadata(metadata_key) == '/url/'


def test_method_state_many():

    winter_app = WinterApplication()

    def query_param(param: str):
        metadata_key = MetadataKey('query', many=True)
        state_value = param
        return functools.partial(winter_app.component_method, metadata_key=metadata_key, state_value=state_value)

    @winter_app.component
    class SimpleComponent:

        @query_param('first')
        @query_param('second')
        def simple_method(self):
            return None

    metadata_key = MetadataKey('query', many=True)

    param = SimpleComponent.simple_method.get_metadata(metadata_key)
    assert param == ['second', 'first']
