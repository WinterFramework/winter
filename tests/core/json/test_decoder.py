import dataclasses
import datetime
import decimal
import enum
import uuid
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import Union

import pytest
from dateutil.tz import tzutc

from winter.core.json import JSONDecodeException
from winter.core.json import Undefined
from winter.core.json import json_decode

empty = object()


class Id(int):
    pass


class Uid(uuid.UUID):
    pass


class Number(decimal.Decimal):
    pass


class Status(enum.Enum):
    SUPER = 'super'
    NOT_SUPER = 'not_super'

class IntStatus(enum.IntEnum):
    SUPER = 1
    NOT_SUPER = 2


@dataclasses.dataclass(frozen=True)
class Contact:
    phones: Set[int]


@dataclasses.dataclass(frozen=True)
class User:
    id: Id
    status: Status
    int_status: IntStatus
    birthday: datetime.date
    contact: Contact
    emails: List[str] = dataclasses.field(default_factory=list)
    created_at: Optional[datetime.datetime] = None
    name: str = 'test name'


@dataclasses.dataclass(frozen=True)
class Profile:
    email: str = empty


@pytest.mark.parametrize(
    ('data', 'expected_instance'), (
        (
            {
                'id': '1',
                'status': 'super',
                'int_status': '1',
                'birthday': '2017-12-21',
                'name': 'name',
                'created_at': '2001-02-03T04:05:06Z',
                'emails': ['test@test.ru'],
                'contact': {
                    'phones': ['123', '456'],
                },
            },
            User(
                Id(1),
                Status.SUPER,
                IntStatus.SUPER,
                datetime.date(year=2017, day=21, month=12),
                Contact({123, 456}),
                ['test@test.ru'],
                datetime.datetime(year=2001, month=2, day=3, hour=4, minute=5, second=6, tzinfo=tzutc()),
                'name',
            ),
        ),
        (
            {
                'id': 1,
                'status': 'super',
                'int_status': '1',
                'birthday': '2017-12-21',
                'contact': {
                    'phones': ['123', '456'],
                },
            },
            User(
                Id(1),
                Status.SUPER,
                IntStatus.SUPER,
                datetime.date(year=2017, day=21, month=12),
                Contact({123, 456}),
                [],
                name='test name',
            ),
        ),
    ),
)
def test_decode(data, expected_instance):
    instance = json_decode(data, User)
    assert instance == expected_instance

    for field in dataclasses.fields(User):
        instance_data = getattr(instance, field.name)
        expected_data = getattr(expected_instance, field.name)

        assert instance_data == expected_data, field.name


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_instance'), (
        (['super'], Set[Status], {Status.SUPER}),
        ([1], Set, {1}),
    ),
)
def test_decode_set(data, type_, expected_instance):
    instance = json_decode(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_instance'), (
        (['super'], Sequence[Status], [Status.SUPER]),
        ([1], Sequence, [1]),
    ),
)
def test_decode_sequence(data, type_, expected_instance):
    instance = json_decode(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_instance'), (
        (None, Optional[Status], None),
        ('super', Optional[Status], Status.SUPER),
    ),
)
def test_decode_optional(data, type_, expected_instance):
    instance = json_decode(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_errors'), (
        (
            ['invalid_status'],
            Set[Status],
            'Value not in allowed values("super", "not_super"): "invalid_status"',
        ),
        (1, Set[Status], 'Cannot decode "1" to set'),
        (None, Set[Status], 'Cannot decode "None" to set'),
        ([[]], Set, 'Cannot decode "[[]]" to set'),
    ),
)
def test_decode_set_with_errors(data, type_, expected_errors):
    with pytest.raises(JSONDecodeException) as ex:
        json_decode(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_instance'), (
        (['super'], List[Status], [Status.SUPER]),
        (['1'], List[IntStatus], [IntStatus.SUPER]),
        ([1], List[IntStatus], [IntStatus.SUPER]),
        ({1}, List, [1]),
        ({1}, list, [1]),
    ),
)
def test_decode_list(data, type_, expected_instance):
    instance = json_decode(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_errors'), (
        (
            ['invalid_status'],
            List[Status],
            'Value not in allowed values("super", "not_super"): "invalid_status"',
        ),
        (1, List[Status], 'Cannot decode "1" to list'),
        (None, List[Status], 'Cannot decode "None" to list'),
        (None, List[IntStatus], 'Cannot decode "None" to list'),
        (['a'], List[IntStatus], 'Value not in allowed values("1", "2"): "a"'),
    ),
)
def test_decode_list_with_errors(data, type_, expected_errors):
    with pytest.raises(JSONDecodeException) as ex:
        json_decode(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_errors'), (
        ([], str, 'Cannot decode "[]" to string'),
        (1, str, 'Cannot decode "1" to string'),
    ),
)
def test_decode_string_with_errors(data, type_, expected_errors):
    with pytest.raises(JSONDecodeException) as ex:
        json_decode(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_instance'), (
        (['super'], Tuple[Status], (Status.SUPER,)),
        ({1}, Tuple, (1,)),
        ({1}, tuple, (1,)),
    ),
)
def test_decode_tuple(data, type_, expected_instance):
    instance = json_decode(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_errors'), (
        (
            ['invalid_status'],
            Tuple[Status],
            'Value not in allowed values("super", "not_super"): "invalid_status"',
        ),
        (1, Tuple[Status], 'Cannot decode "1" to list'),
        (None, Tuple[Status], 'Cannot decode "None" to list'),
    ),
)
def test_decode_tuple_with_errors(data, type_, expected_errors):
    with pytest.raises(JSONDecodeException) as ex:
        json_decode(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_errors'), (
        (1, datetime.datetime, 'Cannot decode "1" to datetime'),
        ('invalid date', datetime.datetime, 'Cannot decode "invalid date" to datetime'),
        (None, datetime.datetime, 'Cannot decode "None" to datetime'),
    ),
)
def test_decode_datetime_with_errors(data, type_, expected_errors):
    with pytest.raises(JSONDecodeException) as ex:
        json_decode(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_errors'), (
        (1, datetime.date, 'Cannot decode "1" to date'),
        ('invalid date', datetime.date, 'Cannot decode "invalid date" to date'),
        (None, datetime.date, 'Cannot decode "None" to date'),
    ),
)
def test_decode_date_with_errors(data, type_, expected_errors):
    with pytest.raises(JSONDecodeException) as ex:
        json_decode(data, type_)
    assert ex.value.errors == expected_errors


def test_decode_without_decoder():
    data = '123'
    type_ = object
    expected_errors = {'non_field_error': 'Invalid type.'}
    with pytest.raises(JSONDecodeException) as ex:
        json_decode(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_instance'), (
        ({'email': 'test'}, Profile, Profile('test')),
        ({}, Profile, Profile()),
    ),
)
def test_decode_dataclass(data, type_, expected_instance):
    instance = json_decode(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_errors'), (
        (
            1, Contact, {
                'non_field_error': 'Invalid type. Need: "object". Got: "1"',
            },
        ),
        (
            {}, Contact, {
                'non_field_error': 'Missing fields: "phones"',
            },
        ),
        (
            {
                'phones': ['invalid_integer'],
            },
            Contact,
            {
                'phones': 'Cannot decode "invalid_integer" to integer',
            },
        ),
        (
            {
                'contact': {
                    'phones': 123,
                },
            },
            User,
            {
                'non_field_error': 'Missing fields: "id", "status", "int_status", "birthday"',
                'contact': {
                    'phones': 'Cannot decode "123" to set',
                },
            },
        ),

    ),
)
def test_decode_dataclass_with_errors(data, type_, expected_errors):
    with pytest.raises(JSONDecodeException) as ex:
        json_decode(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_instance'), (
        ('8bd5b7f9-3cd3-4a7e-be17-23df921b7fb7', uuid.UUID, uuid.UUID('8bd5b7f9-3cd3-4a7e-be17-23df921b7fb7')),
        ('8bd5b7f9-3cd3-4a7e-be17-23df921b7fb7', Uid, Uid('8bd5b7f9-3cd3-4a7e-be17-23df921b7fb7')),
    ),
)
def test_decode_uuid(data, type_, expected_instance):
    instance = json_decode(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_errors'), (
        ('invalid uuid', uuid.UUID, 'Cannot decode "invalid uuid" to uuid'),
        ('invalid uuid', Uid, 'Cannot decode "invalid uuid" to uuid'),
    ),
)
def test_decode_uuid_with_errors(data, type_, expected_errors):
    with pytest.raises(JSONDecodeException) as ex:
        json_decode(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_instance'), (
        ('1.05', decimal.Decimal, decimal.Decimal('1.05')),
        (1.1, Number, Number(1.1)),
    ),
)
def test_decode_decimal(data, type_, expected_instance):
    instance = json_decode(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_errors'), (
        (None, decimal.Decimal, 'Cannot decode "None" to decimal'),
        ('invalid decimal', Number, 'Cannot decode "invalid decimal" to decimal'),
    ),
)
def test_decode_decimal_with_errors(data, type_, expected_errors):
    with pytest.raises(JSONDecodeException) as ex:
        json_decode(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_errors'), (
        (None, float, 'Cannot decode "None" to float'),
        ('invalid decimal', float, 'Cannot decode "invalid decimal" to float'),
    ),
)
def test_decode_float_with_errors(data, type_, expected_errors):
    with pytest.raises(JSONDecodeException) as ex:
        json_decode(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_instance'), (
        ({'data': 1}, dict, {'data': 1}),
        ({'data': 1}, Dict, {'data': 1}),
        ({'1': '1'}, Dict[int, int], {1: 1}),
    ),
)
def test_decode_dict(data, type_, expected_instance):
    instance = json_decode(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_errors'), (
        (None, dict, 'Cannot decode "None" to object'),
        (None, Dict, 'Cannot decode "None" to object'),
        ('invalid object', dict, 'Cannot decode "invalid object" to object'),
        ({'data1': 1}, Dict[int, int], 'Cannot decode "data1" to integer'),
        ({1: 'data2'}, Dict[float, float], 'Cannot decode "data2" to float'),
    ),
)
def test_decode_dict_with_errors(data, type_, expected_errors):
    with pytest.raises(JSONDecodeException) as ex:
        json_decode(data, type_)
    assert ex.value.errors == expected_errors


def test_decode_any():
    instance = object()
    assert json_decode(instance, Any) is instance


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_instance'), (
        (True, bool, True),
        (False, bool, False),
        ('True', bool, True),
        ('true', bool, True),
        ('false', bool, False),
        ('False', bool, False),
        (1, bool, True),
        (1.0, bool, True),
        (0, bool, False),
        (0.0, bool, False),
    ),
)
def test_decode_bool(data, type_, expected_instance):
    instance = json_decode(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_errors'), (
        ('', bool, 'Cannot decode "" to bool'),
        ('invalid_bool', bool, 'Cannot decode "invalid_bool" to bool'),
    ),
)
def test_decode_bool_with_errors(data, type_, expected_errors):
    with pytest.raises(JSONDecodeException) as ex:
        json_decode(data, type_)
    assert ex.value.errors == expected_errors


@dataclasses.dataclass
class DataclassWithUndefinedType:
    a: Union[int, Undefined]


@dataclasses.dataclass
class DataclassWithUndefinedByDefault:
    a: Union[int, Undefined] = Undefined()


@pytest.mark.parametrize(
    ('data', 'type_', 'expected_result'), (
        ({}, DataclassWithUndefinedType, DataclassWithUndefinedType(a=Undefined())),
        ({'a': 123}, DataclassWithUndefinedType, DataclassWithUndefinedType(a=123)),
        ({}, DataclassWithUndefinedByDefault, DataclassWithUndefinedByDefault(a=Undefined())),
        ({'a': 123}, DataclassWithUndefinedByDefault, DataclassWithUndefinedByDefault(a=123)),
    ),
)
def test_decode_dataclass_with_no_value(data, type_, expected_result):
    instance = json_decode(data, type_)
    assert instance == expected_result
