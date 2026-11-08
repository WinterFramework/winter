import mock

from winter.application.module_discovery import get_all_subclasses


def test_all_subclasses():
    exception_subclasses = list(get_all_subclasses(Exception))
    assert ('OverflowError', OverflowError) in exception_subclasses


@mock.patch('_weakref.ReferenceType')
def test_all_subclasses_with_exception(reference_type):
    reference_type.side_effect = TypeError
    exception_subclasses = list(get_all_subclasses(Exception))
    assert not exception_subclasses
