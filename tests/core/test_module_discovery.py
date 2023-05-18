import mock

from winter.core import Component
from winter.core.module_discovery import get_all_classes
from winter.core.module_discovery import get_all_subclasses
from winter.web import Configurer


def test_module_import():
    found_classes = list(get_all_classes('winter.web'))
    # Verifying that some class (it can be any class) could be found
    assert ('Configurer', Configurer) in found_classes
    assert ('Component', Component) not in found_classes


@mock.patch('inspect.getmembers')
def test_module_import_with_exception(getmembers):
    # Verifying that import error during search of class will not stop the search
    getmembers.side_effect = ImportError
    found_classes = list(get_all_classes('winter.core'))
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
