from http import HTTPStatus

import pytest

from winter.web import problem
from winter_openapi import validate_missing_raises_annotations


def test_validate_missing_raises_annotations_with_missed_raises_and_not_global_expect_assert_exception():
    @problem(HTTPStatus.BAD_REQUEST)
    class MissingException(Exception):
        pass
    expected_error_message = f'You are missing declaration for next exceptions: {MissingException.__name__}'

    with pytest.raises(AssertionError, match=expected_error_message):
        validate_missing_raises_annotations()
