from winter.core.json import Undefined


def test_undefined():
    assert Undefined() == Undefined()
    assert Undefined() != 1
    assert Undefined() != ''
    assert Undefined() is not None
    assert repr(Undefined()) == 'Undefined'
    assert {Undefined(), Undefined()} == {Undefined()}
