import datetime
import decimal
import enum
import json

import pytest
import pytz
import uuid

from winter.json_encoder import JSONEncoder


class Id(int):
    pass


class Enum(enum.Enum):
    NUMBER = 1
    FLOAT = 1.0
    TUPLE = ('000', 1)
    LIST = [12]
    SET = {'11'}
    STRING = 'test string'



def get_encoder_class():
    return JSONEncoder


@pytest.mark.parametrize(('value', 'expected_value'), [
    (1, 1),
    (Id(1), 1),
    (Enum.NUMBER, 1),
    (Enum.FLOAT, 1.0),
    (Enum.TUPLE, ['000', 1]),
    (Enum.LIST, [12]),
    (Enum.SET, ['11']),
    (Enum.STRING, 'test string'),
    (datetime.datetime(year=2019, month=1, day=1, tzinfo=pytz.UTC, hour=3), '2019-01-01T03:00:00Z'),
    (datetime.date(year=2019, month=1, day=1), '2019-01-01'),
    (datetime.time(hour=3, minute=50, second=20), '03:50:20'),
    (datetime.timedelta(hours=10, seconds=20), str(10 * 60 * 60 + 20.0)),
    (decimal.Decimal(11.0), 11.0),
    (uuid.UUID('c010de13-7f2d-41f9-b4f0-893087e32b92'), 'c010de13-7f2d-41f9-b4f0-893087e32b92'),
    (b'test bytes', 'test bytes'),
])
def test_int(value, expected_value):
    encoder_class = get_encoder_class()
    data = {'key': value}
    assert expected_value == json.loads(json.dumps(data, cls=encoder_class))['key']
