import mock

from winter.components import Component
from winter.application.module_discovery import get_all_classes
from winter.application.module_discovery import get_all_subclasses


def test_module_import():
    found_classes = list(get_all_classes('winter.web'))
    # Verifying that some class (it can be any class) could be found
    assert ('Component', Component) not in found_classes


@mock.patch('inspect.getmembers')
def test_module_import_with_exception(getmembers):
    # Verifying that import error during search of class will not stop the search
    getmembers.side_effect = ImportError
    found_classes = list(get_all_classes('winter.components'))
    # It can't find any class, because we have ImportError on any class
    assert not found_classes


def test_all_subclasses():
    exception_subclasses = list(get_all_subclasses(Exception))
    assert ('OverflowError', OverflowError) in exception_subclasses


@mock.patch('_weakref.ReferenceType')
def test_all_subclasses_with_exception(reference_type):
    reference_type.side_effect = TypeError
    exception_subclasses = list(get_all_subclasses(Exception))
    assert not exception_subclasses


def test_get_all_classes_of_module():
    from tests.application.discovery.sample import Sample

    found_classes = list(get_all_classes('tests.application.discovery.sample'))

    # SampleHelper is imported into the module but defined in a module whose name only starts the same
    assert found_classes == [('Sample', Sample)]


def test_get_all_classes_of_package():
    from tests.application.discovery.sample import Sample
    from tests.application.discovery.sample_helpers import SampleHelper

    found_classes = list(get_all_classes('tests.application.discovery'))

    assert sorted(found_classes) == [('Sample', Sample), ('SampleHelper', SampleHelper)]
