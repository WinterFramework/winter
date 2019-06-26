import datetime
import enum
import typing

import dataclasses
import pytest
from dateutil.tz import tzutc

from winter.converters.converter import ConvertError
from winter.converters.converter import convert


class Id(int):
    pass


class Status(enum.Enum):
    SUPER = 'super'
    NOT_SUPER = 'not_super'


@dataclasses.dataclass(frozen=True)
class Contact:
    phones: typing.Set[int]


@dataclasses.dataclass(frozen=True)
class User:
    id: Id
    status: Status
    birthday: datetime.date
    emails: typing.List[str]
    contact: Contact
    created_at: typing.Optional[datetime.datetime] = None
    name: typing.Optional[str] = None


@pytest.mark.parametrize(('data', 'expected_instance'), (
    (
        {
            'id': '1',
            'status': 'super',
            'birthday': '2017-12-21',
            'name': 'name',
            'created_at': '2001-02-03T04:05:06Z',
            'emails': ['test@test.ru'],
            'contact': {'phones': ['123', '456']}
        },
        User(
            Id(1),
            Status.SUPER,
            datetime.date(year=2017, day=21, month=12),
            ['test@test.ru'],
            Contact({123, 456}),
            datetime.datetime(year=2001, month=2, day=3, hour=4, minute=5, second=6, tzinfo=tzutc()),
            'name',
        )
    ),
    (
        {
            'id': 1,
            'status': 'super',
            'birthday': '2017-12-21',
            'emails': ['test@test.ru'],
            'contact': {'phones': ['123', '456']}
        },
        User(
            Id(1),
            Status.SUPER,
            datetime.date(year=2017, day=21, month=12),
            ['test@test.ru'],
            Contact({123, 456}),
        )
    ),
))
def test_converter(data, expected_instance):
    instance = convert(data, User)
    assert instance == expected_instance

    for field in dataclasses.fields(User):
        instance_data = getattr(instance, field.name)
        expected_data = getattr(expected_instance, field.name)

        assert instance_data == expected_data, field.name


@pytest.mark.parametrize(('data', 'type_', 'expected_instance'), (
    (['super'], typing.Set[Status], {Status.SUPER}),
))
def test_convert_set(data, type_, expected_instance):
    instance = convert(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(('data', 'type_', 'expected_errors'), (
    (['invalid_status'], typing.Set[Status], 'Value not in allowed values("super", "not_super"): "invalid_status"'),
    (1, typing.Set[Status], 'Cannot convert "1" to set'),
    (None, typing.Set[Status], 'Cannot convert "None" to set'),
))
def test_convert_set_with_errors(data, type_, expected_errors):
    with pytest.raises(ConvertError) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(('data', 'type_', 'expected_errors'), (
    (['invalid_status'], typing.List[Status], 'Value not in allowed values("super", "not_super"): "invalid_status"'),
    (1, typing.List[Status], 'Cannot convert "1" to list'),
    (None, typing.List[Status], 'Cannot convert "None" to list'),
))
def test_convert_list_with_errors(data, type_, expected_errors):
    with pytest.raises(ConvertError) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(('data', 'type_', 'expected_errors'), (
    (1, datetime.datetime, 'Cannot convert "1" to datetime'),
    ('invalid date', datetime.datetime, 'Cannot convert "invalid date" to datetime'),

))
def test_convert_datetime_with_errors(data, type_, expected_errors):
    with pytest.raises(ConvertError) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(('data', 'type_', 'expected_errors'), (
    (1, datetime.date, 'Cannot convert "1" to date'),
    ('invalid date', datetime.date, 'Cannot convert "invalid date" to date'),
))
def test_convert_date_with_errors(data, type_, expected_errors):
    with pytest.raises(ConvertError) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


def test_convert_without_converter():
    data = '123'
    type_ = object
    expected_errors = 'Cannot convert "123"'
    with pytest.raises(ConvertError) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(('data', 'type_', 'expected_errors'), (
    (1, Contact, 'Cannot convert "1"'),
    ({}, Contact, {'non_field_error': 'Missing fields: "phones"'}),
    ({'phones': ['invalid_integer']}, Contact, {'phones': 'Cannot convert "invalid_integer" to integer'}),
    (
        {'contact': {'phones': 123}},
        User,
        {
            'non_field_error': 'Missing fields: "id", "status", "birthday", "emails"',
            'contact': {'phones': 'Cannot convert "123" to set'},
        },
    ),

))
def test_convert_dataclasss_with_errors(data, type_, expected_errors):
    with pytest.raises(ConvertError) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors
