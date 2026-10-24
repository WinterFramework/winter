from http import HTTPStatus

import pytest

import winter.openapi
import winter.web
from winter.application import Application
from winter.application import get_injector
from winter.web import problem
from winter.web.routing import get_route
from winter.openapi.generator import generate_openapi_for_routes
from winter.openapi import validate_missing_raises_annotations


def test_validate_missing_raises_annotations_with_missed_raises_and_not_global_expect_assert_exception():
    @problem(HTTPStatus.BAD_REQUEST)
    class MissingException(Exception):
        pass
    app = Application(modules=[], injector=get_injector())
    app.add(MissingException)
    expected_error_message = f'You are missing declaration for next exceptions: {MissingException.__name__}'

    with pytest.raises(AssertionError, match=expected_error_message):
        validate_missing_raises_annotations(app)


@pytest.mark.parametrize('validate', [True, False])
def test_validate_spec(validate):
    """
    There is no way to check the case when the spec is invalid.
    So it's mostly to execute both branches of the code and check that it doesn't fail.
    """
    class _TestAPI:
        @winter.web.route_get('/test-api/')
        def endpoint(self):  # pragma: no cover
            pass

    route = get_route(_TestAPI.endpoint)

    # Act
    generate_openapi_for_routes(title='title', version='1.0.0', routes=[route], validate=validate)


def test_validate_missing_raises_annotations_with_declared_and_global_exceptions():
    @problem(HTTPStatus.BAD_REQUEST)
    class DeclaredException(Exception):
        pass

    @winter.openapi.global_exception
    @problem(HTTPStatus.BAD_REQUEST)
    class GlobalException(Exception):
        pass

    class _TestAPI:
        @winter.web.raises(DeclaredException)
        @winter.web.route_get('/test-api/')
        def endpoint(self):  # pragma: no cover
            pass

    def not_a_component():  # pragma: no cover
        pass

    app = Application(modules=[], injector=get_injector())
    for definition in [DeclaredException, GlobalException, _TestAPI, not_a_component]:
        app.add(definition)

    # Act
    validate_missing_raises_annotations(app)
