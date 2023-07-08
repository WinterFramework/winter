from http import HTTPStatus

import pytest

import winter
from winter.web import problem
from winter.web.routing import get_route
from winter_openapi import generate_openapi
from winter_openapi import validate_missing_raises_annotations


def test_validate_missing_raises_annotations_with_missed_raises_and_not_global_expect_assert_exception():
    @problem(HTTPStatus.BAD_REQUEST)
    class MissingException(Exception):
        pass
    expected_error_message = f'You are missing declaration for next exceptions: {MissingException.__name__}'

    with pytest.raises(AssertionError, match=expected_error_message):
        validate_missing_raises_annotations()


@pytest.mark.parametrize('validate', [True, False])
def test_validate_spec(validate):
    """
    There is no way to check the case when the spec is invalid.
    So it's mostly to execute both branches of the code and check that it doesn't fail.
    """
    class _TestAPI:
        @winter.route_get('/test-api/')
        def endpoint(self):  # pragma: no cover
            pass

    route = get_route(_TestAPI.endpoint)

    # Act
    generate_openapi(title='title', version='1.0.0', routes=[route], validate=validate)
