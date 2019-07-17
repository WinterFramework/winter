import pytest

import winter.core
from winter.schema import disable_generating_swagger
from winter.schema import enable_generating_swagger
from winter.schema import generate_swagger_for_operation
from winter.schema import is_generating_swagger_enabled
from winter.schema.generation import InvalidReturnTypeException
from winter.schema.generation import build_response_schema


class _enable_generating_swagger_context_manager:

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        enable_generating_swagger()


def test_disable_generating_swagger():
    with _enable_generating_swagger_context_manager():
        # Act
        disable_generating_swagger()

        # Assert
        assert not is_generating_swagger_enabled()


def test_is_generating_swagger_enabled():
    with _enable_generating_swagger_context_manager():
        # Act
        generating_enabled = is_generating_swagger_enabled()

        # Assert
        assert generating_enabled


def test_enable_generating_swagger():
    with _enable_generating_swagger_context_manager():
        # Act
        enable_generating_swagger()

        # Assert
        assert is_generating_swagger_enabled()


def test_generate_swagger_for_operation_with_disabled_generating_swagger():
    with _enable_generating_swagger_context_manager():
        disable_generating_swagger()

        # Act and Assert that nothing happen
        generate_swagger_for_operation(None, None, None)


def test_build_response_shema_with_invalid_return_type():
    expected_repr = (
        'InvalidReturnTypeException(tests.schema.test_generation.Controller.method: '
        "-> <class 'object'>: Unknown type: <class 'object'>)"
    )

    class Controller:

        @winter.core.component_method
        def method(self) -> object:
            return object()

    with pytest.raises(InvalidReturnTypeException) as exception:
        build_response_schema(Controller.method)

    assert repr(exception.value) == expected_repr
