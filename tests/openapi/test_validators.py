from http import HTTPStatus

import pytest

import winter.openapi
import winter.web
from tests.injection import app_injector
from tests.web_application import web_application
from winter.web import problem
from winter.openapi import validate_missing_raises_annotations


def test_validate_missing_raises_annotations_with_missed_raises_and_not_global_expect_assert_exception():
    @problem(HTTPStatus.BAD_REQUEST)
    class MissingException(Exception):
        pass
    app = web_application(MissingException, injector=app_injector)
    expected_error_message = f'You are missing declaration for next exceptions: {MissingException.__name__}'

    with pytest.raises(AssertionError, match=expected_error_message):
        validate_missing_raises_annotations(app)


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

    app = web_application(DeclaredException, GlobalException, _TestAPI, not_a_component, injector=app_injector)

    # Act
    validate_missing_raises_annotations(app)
