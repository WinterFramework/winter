from winter.core.utils import cached_property


class _Entity:

    def __init__(self):
        self._counter = 0

    @cached_property
    def method(self):
        """Docstring"""
        self._counter += 1
        return self._counter


def test_cached_property_getter():
    assert isinstance(_Entity.method, cached_property)
    entity = _Entity()

    for _ in range(5):
        assert entity.method == 1

    assert _Entity.method.__doc__ == 'Docstring'


def test_cached_property_setter():
    entity = _Entity()

    entity.method = 3

    assert entity.method == 3
