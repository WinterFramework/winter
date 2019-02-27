import dataclasses
import pytest

import winter.core
from winter.core import Component
from winter.core import WinterApplication


@dataclasses.dataclass(frozen=True)
class SimpleAnnotation:
    value: str


def simple_annotation(param: str):
    return winter.core.annotate(SimpleAnnotation(param))


def test_is_component():
    winter_app = WinterApplication()

    class SimpleComponent:
        pass

    winter_app.add_component(SimpleComponent)
    assert winter.core.is_component(SimpleComponent)


def test_component_raises():
    with pytest.raises(ValueError):
        winter.core.component(object())


def test_methods():
    class SimpleComponent:

        @winter.core.component_method
        def simple_method(self):
            return self

    component = Component.get_by_cls(SimpleComponent)

    assert len(component.methods) == 1, SimpleComponent.simple_method
    method = component.get_method('simple_method')

    assert method is SimpleComponent.simple_method
    component = SimpleComponent()
    assert SimpleComponent.simple_method(component) is component


def test_method_state():
    class SimpleComponent:

        @simple_annotation('/url/')
        def simple_method(self):
            return 123

    assert SimpleComponent.simple_method.annotations.get(SimpleAnnotation) == [SimpleAnnotation('/url/')]


def test_method_state_many():

    class SimpleComponent:

        @simple_annotation('first')
        @simple_annotation('second')
        def simple_method(self):
            return None

    expected_annotations = [SimpleAnnotation('second'), SimpleAnnotation('first')]
    assert SimpleComponent.simple_method.annotations.get(SimpleAnnotation) == expected_annotations


def test_register_with_instance():
    instance = object()

    with pytest.raises(ValueError) as exception:
        Component.register(instance)

    assert str(exception.value) == f'Need class. Got: {instance}'
    assert exception.value.args == (f'Need class. Got: {instance}',)
