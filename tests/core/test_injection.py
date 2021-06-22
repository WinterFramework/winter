from winter.core import get_injector


def test_get_injector():
    injector = get_injector()
    assert injector is not None


def test_create_object():
    class A:
        pass

    injector = get_injector()
    a = injector.create_object(A)
    assert isinstance(a, A)
