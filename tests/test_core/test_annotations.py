import dataclasses
import pytest

from winter.core import Component
from winter.core import annotate
from winter.core import annotate_class
from winter.core import annotate_method
from winter.core import is_component
from winter.core.annotations import Annotations
from winter.core.annotations import MultipleAnnotationFound
from winter.core.annotations import NotFoundAnnotation


@dataclasses.dataclass(frozen=True)
class SimpleAnnotation:
    path: str


def simple_annotation(string: str):
    return annotate(SimpleAnnotation(string))


def simple_annotation_class(string: str):
    return annotate_class(SimpleAnnotation(string))


def simple_annotation_method(string: str):
    return annotate_method(SimpleAnnotation(string))


@pytest.mark.parametrize('decorator', (simple_annotation, simple_annotation_class))
def test_on_class_by_decorator(decorator):
    @decorator('test')
    class SimpleComponent:
        pass

    assert is_component(SimpleComponent)
    component = Component.get_by_cls(SimpleComponent)
    assert component.annotations.get(SimpleAnnotation) == [SimpleAnnotation('test')]


@pytest.mark.parametrize('decorator', (simple_annotation, simple_annotation_method))
def test_on_method_by_decorator(decorator):
    class SimpleComponent:

        @decorator('test')
        def method(self):
            pass

    assert SimpleComponent.method.annotations.get(SimpleAnnotation) == [SimpleAnnotation('test')]


def test_get_one_not_found():
    annotations_ = Annotations()

    with pytest.raises(NotFoundAnnotation) as exception:
        annotations_.get_one(SimpleAnnotation)

    assert exception.value.annotation_type == SimpleAnnotation
    assert str(exception.value) == f'Not found annotation for {SimpleAnnotation}'


def test_get_one_multiple_raises():
    annotations_ = Annotations()
    annotations_.add(SimpleAnnotation('first'))
    annotations_.add(SimpleAnnotation('second'))

    with pytest.raises(MultipleAnnotationFound) as exception:
        annotations_.get_one(SimpleAnnotation)

    assert exception.value.annotation_type == SimpleAnnotation
    assert str(exception.value) == f'Found more than one annotation for {SimpleAnnotation}: 2'


def test_get_one():
    annotations_ = Annotations()
    annotations_.add(SimpleAnnotation('first'))

    annotation = annotations_.get_one(SimpleAnnotation)

    assert annotation == SimpleAnnotation('first')


@pytest.mark.parametrize(('decorator_factory', 'error_message_template'), (
        (annotate, 'Need function or class. Got: {instance}'),
        (annotate_class, 'Need class. Got: {instance}'),
        (annotate_method, 'Need function. Got: {instance}'),
))
def test_annotate_with_instance(decorator_factory, error_message_template):
    instance = object()

    decorator = decorator_factory(SimpleAnnotation('string'))

    with pytest.raises(ValueError) as exception:
        decorator(instance)

    assert str(exception.value) == error_message_template.format(instance=instance)
