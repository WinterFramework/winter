from winter.core.utils import cached_property


def test_cached_property():
    class _Test:

        @cached_property
        def method(self):
            """Docstring"""
            return 1

    assert isinstance(_Test.method, cached_property)
    assert _Test().method == 1
    assert _Test.method.__doc__ == 'Docstring'
