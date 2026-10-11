from winter.application import get_injector


def test_get_injector():
    injector = get_injector()
    assert injector is not None
