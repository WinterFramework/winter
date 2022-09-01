import mock

from winter.core import WinterApplication
from winter.core.module_discovery import get_all_subclasses
from winter.core.module_discovery import get_all_classes


def test_module_import():
    found_classes = get_all_classes()
    # Verifying that some class (it can be any class) could be found
    assert ('WinterApplication', WinterApplication) in found_classes


@mock.patch('inspect.getmembers')
def test_module_import_with_exception(getmembers):
    # Verifying that import error during search of class will not stop the search
    getmembers.side_effect = ImportError
    found_classes = get_all_classes()
    # It can't find any class, beacuse we have ImportError on any class
    assert not found_classes


def test_all_subclasses():
    exception_subclasses = get_all_subclasses(Exception)
    assert ('OverflowError', OverflowError) in exception_subclasses


@mock.patch('_weakref.ReferenceType')
def test_all_subclasses_with_exception(reference_type):
    reference_type.side_effect = TypeError
    exception_subclasses = get_all_subclasses(Exception)
    assert not exception_subclasses
