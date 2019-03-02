from winter.core.utils import cached_property


def test_cached_property():
    class _Test:

        @cached_property
        def method(self):
            return 1

    assert isinstance(_Test.method, cached_property)
    assert _Test().method == 1
