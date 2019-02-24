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
