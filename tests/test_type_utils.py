from collections.abc import Iterable
from types import UnionType
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import pytest

from winter.core.utils.typing import get_origin_type
from winter.core.utils.typing import get_type_name
from winter.core.utils.typing import is_iterable_type
from winter.core.utils.typing import is_optional
from winter.core.utils.typing import is_origin_type_subclasses
from winter.core.utils.typing import is_union


@pytest.mark.parametrize(
    ('typing_for_check', 'expected'), [
        (Optional[List[int]], True),
        (Union[List[int], Tuple], True),
        (Union[List | Tuple], True),
        (Union[list | tuple], True),
        (int, False),
        (str, False),
        (Optional[List[int]], True),
        (Union[List, str], False),
    ],
)
def test_is_iterable_type(typing_for_check, expected):
    assert is_iterable_type(typing_for_check) == expected


@pytest.mark.parametrize(
    ('typing_for_check', 'expected'), [
        (Optional[int], True),
        (Union[List, Tuple], True),
        (Union[list, tuple], True),
        (Tuple, False),
        (Union, True),
    ],
)
def test_is_union(typing_for_check, expected):
    assert is_union(typing_for_check) == expected


@pytest.mark.parametrize(
    ('typing_for_check', 'expected'), [
        (Optional[int], True),
        (Union[int, None], True),
        (int | None, True),
        (Union[int, list], False),
        (int | list, False),
        (int, False),
        (Union, False),
    ],
)
def test_is_optional(typing_for_check, expected):
    assert is_optional(typing_for_check) == expected


@pytest.mark.parametrize(
    ('typing_for_check', 'expected'), [
        (int, int),
        (Union[int], int),
        (Union[int, float], Union),
        (int | float, UnionType),
    ],
)
def test_get_origin_type(typing_for_check, expected):
    assert get_origin_type(typing_for_check) == expected


@pytest.mark.parametrize(
    ('typing_for_check', 'subclasses_type', 'expected'), [
        (Union[int], int, True),
        (List, Iterable, True),
        (List[int], Iterable, True),
        (list[int], Iterable, True),
    ],
)
def test_is_origin_type_subclasses(typing_for_check, subclasses_type, expected):
    assert is_origin_type_subclasses(typing_for_check, subclasses_type) == expected
    assert is_origin_type_subclasses(List, Iterable) == expected
    assert is_origin_type_subclasses(List[int], Iterable) == expected


@pytest.mark.parametrize(
    ('type_', 'expected_type_name'), [
        (int, 'int'),
        (Dict[int, str], 'Dict[int, str]'),
        (Tuple[int], 'Tuple[int]'),
        (List[int], 'List[int]'),
        (Optional[str], 'Optional[str]'),
        (Union[int, str], 'Union[int, str]'),
        (dict[int, str], 'dict[int, str]'),
        (tuple[int], 'tuple[int]'),
        (list[int], 'list[int]'),
        (int | str, 'int | str'),
        (1, 'int'),
    ],
)
def test_get_type_name(type_, expected_type_name):
    assert expected_type_name == get_type_name(type_)
