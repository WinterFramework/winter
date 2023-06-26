import pytest

import winter.core
from winter_openapi.generation import CanNotInspectReturnType
from winter_openapi.generation import build_response_schema


class TestAPI:
    @winter.core.component_method
    def with_invalid_return_type(self) -> object:  # pragma: no cover
        pass


def test_with_invalid_return_type():

    with pytest.raises(CanNotInspectReturnType) as e:
        build_response_schema(TestAPI.with_invalid_return_type)

    assert repr(e.value) == (
        'CanNotInspectReturnType(test_build_response_schema.TestAPI.with_invalid_return_type: '
        "-> <class 'object'>: Unknown type: <class 'object'>)"
    )
