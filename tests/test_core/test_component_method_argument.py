import pytest

from winter.core import ArgumentDoesNotHaveDefault
from winter.core import ComponentMethod


def test_parameter():
    def test(number: int) -> int:
        return number

    method = ComponentMethod(test)
    argument = method.get_argument('number')
    parameter = argument.parameter
    assert parameter.name == 'number'
    assert parameter.annotation == int
    assert parameter.kind == parameter.POSITIONAL_OR_KEYWORD


def test_default():
    def test(number: int) -> int:
        return number

    method = ComponentMethod(test)
    argument = method.get_argument('number')

    with pytest.raises(ArgumentDoesNotHaveDefault) as exception:
        argument.get_default()

    assert str(exception.value) == f'{argument} does not have get_default'
