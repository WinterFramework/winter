from collections.abc import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import pytest

from winter.type_utils import get_origin_type
from winter.type_utils import is_iterable
from winter.type_utils import is_optional
from winter.type_utils import is_origin_type_subclasses
from winter.type_utils import is_union


@pytest.mark.parametrize(('typing_for_check', 'expected'), [
    (Optional[List[int]], True),
    (Union[List[int], Tuple], True),
    (int, False),
    (str, False),
    (Optional[List[int]], True),
    (Union[List, str], False),
])
def test_is_iterable(typing_for_check, expected):
    assert is_iterable(typing_for_check) == expected


@pytest.mark.parametrize(('typing_for_check', 'expected'), [
    (Optional[int], True),
    (Union[List, Tuple], True),
    (Tuple, False),
    (Union, True),
])
def test_is_union(typing_for_check, expected):
    assert is_union(typing_for_check) == expected


@pytest.mark.parametrize(('typing_for_check', 'expected'), [
    (Optional[int], True),
    (Union[int, None], True),
    (Union[int, list], False),
    (int, False),
])
def test_is_optional(typing_for_check, expected):
    assert is_optional(typing_for_check) == expected


@pytest.mark.parametrize(('typing_for_check', 'expected'), [
    (int, int),
    (Union[int], int),
    (Union[int, float], Union),
])
def test_get_origin_type(typing_for_check, expected):
    assert get_origin_type(typing_for_check) == expected


@pytest.mark.parametrize(('typing_for_check', 'subclasses_type', 'expected'), [
    (Union[int], int, True),
    (List, Iterable, True),
    (List[int], Iterable, True),
])
def test_is_origin_type_subclasses(typing_for_check, subclasses_type, expected):
    assert is_origin_type_subclasses(typing_for_check, subclasses_type) == expected
    assert is_origin_type_subclasses(List, Iterable) == expected
    assert is_origin_type_subclasses(List[int], Iterable) == expected
