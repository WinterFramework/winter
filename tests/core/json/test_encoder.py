import datetime
import decimal
import enum
import json
import uuid
from dataclasses import dataclass

import pytest
import pytz
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy

from winter.core.json import JSONEncoder


class Id(int):
    pass


class Enum(enum.Enum):
    ID = Id(1)
    NUMBER = 2
    FLOAT = 3.0
    TUPLE = ('000', 1)
    ARRAY = ['000', 1]
    STRING = 'test string'


@dataclass
class NestedDataclass:
    nested_number: int


@dataclass
class Dataclass:
    id_: Id
    number: int
    string: str
    date: datetime.date
    nested: NestedDataclass


def generator():
    yield Enum.NUMBER


@pytest.mark.parametrize(
    ('value', 'expected_value'), [
        (None, None),
        (1, 1),
        ([], []),
        (frozenset(), []),
        (generator(), [2]),
        (set(), []),
        (Id(1), 1),
        (gettext_lazy('translated_text'), 'translated_text'),
        (gettext('translated_text'), 'translated_text'),
        (Enum.ID, 1),
        (Enum.NUMBER, 2),
        (Enum.FLOAT, 3.0),
        (Enum.TUPLE, ['000', 1]),
        (Enum.ARRAY, ['000', 1]),
        (Enum.STRING, 'test string'),
        (datetime.datetime(year=2019, month=1, day=1, hour=3), '2019-01-01T03:00:00'),
        (datetime.datetime(year=2019, month=1, day=1, tzinfo=pytz.UTC, hour=3), '2019-01-01T03:00:00Z'),
        (datetime.date(year=2019, month=1, day=1), '2019-01-01'),
        (datetime.time(hour=3, minute=50, second=20), '03:50:20'),
        (datetime.timedelta(hours=10, seconds=20), str(10 * 60 * 60 + 20.0)),
        (decimal.Decimal('11.0'), '11.0'),
        (uuid.UUID('c010de13-7f2d-41f9-b4f0-893087e32b92'), 'c010de13-7f2d-41f9-b4f0-893087e32b92'),
        (b'test bytes', 'test bytes'),
        (
            Dataclass(
                Id(1),
                1,
                'test',
                datetime.date(year=2019, month=1, day=1),
                NestedDataclass(10),
            ), {'id_': 1, 'number': 1, 'string': 'test', 'date': '2019-01-01', 'nested': {'nested_number': 10}},
        ),
    ],
)
def test_encoder(value, expected_value):
    assert expected_value == json.loads(json.dumps(value, cls=JSONEncoder))


@pytest.mark.parametrize(
    ('value', 'exception_type', 'exception_messages'), (
        (
            datetime.time(hour=3, minute=50, second=20, tzinfo=pytz.UTC),
            ValueError,
            ("JSON can't represent timezone-aware times.",),
        ),
        (
            object(),
            TypeError,
            (
                f"Object of type '{object.__name__}' is not JSON serializable",
                f'Object of type {object.__name__} is not JSON serializable',
            ),
        ),
    ),
)
def test_encoder_with_raises(value, exception_type, exception_messages):
    data = {'key': value}

    with pytest.raises(exception_type) as exception:
        json.dumps(data, cls=JSONEncoder)

    assert exception.value.args[0] in exception_messages
