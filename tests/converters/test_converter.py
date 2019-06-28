import datetime
import decimal
import enum
import typing
import uuid

import dataclasses
import pytest
from dateutil.tz import tzutc

from winter.converters.converter import ConvertException
from winter.converters.converter import convert


class Id(int):

    def __eq__(self, other):
        if not isinstance(other, __class__):
            return False
        return super().__eq__(other)


class Uid(uuid.UUID):

    def __eq__(self, other):
        if not isinstance(other, __class__):
            return False
        return super().__eq__(other)


class Number(decimal.Decimal):

    def __eq__(self, other):
        if not isinstance(other, __class__):
            return False
        return super().__eq__(other)


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
    name: str = 'test name'


@pytest.mark.parametrize(('data', 'expected_instance'), (
    (
        {
            'id': '1',
            'status': 'super',
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
            datetime.date(year=2017, day=21, month=12),
            ['test@test.ru'],
            Contact({123, 456}),
            datetime.datetime(year=2001, month=2, day=3, hour=4, minute=5, second=6, tzinfo=tzutc()),
            'name',
        ),
    ),
    (
        {
            'id': 1,
            'status': 'super',
            'birthday': '2017-12-21',
            'emails': ['test@test.ru'],
            'contact': {
                'phones': ['123', '456'],
            },
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
def test_convert(data, expected_instance):
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
    (
        ['invalid_status'],
        typing.Set[Status],
        'Value not in allowed values("super", "not_super"): "invalid_status"'
    ),
    (1, typing.Set[Status], 'Cannot convert "1" to set'),
    (None, typing.Set[Status], 'Cannot convert "None" to set'),
))
def test_convert_set_with_errors(data, type_, expected_errors):
    with pytest.raises(ConvertException) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(('data', 'type_', 'expected_errors'), (
    (
        ['invalid_status'],
        typing.List[Status],
        'Value not in allowed values("super", "not_super"): "invalid_status"'
    ),
    (1, typing.List[Status], 'Cannot convert "1" to list'),
    (None, typing.List[Status], 'Cannot convert "None" to list'),
))
def test_convert_list_with_errors(data, type_, expected_errors):
    with pytest.raises(ConvertException) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(('data', 'type_', 'expected_errors'), (
    (1, datetime.datetime, 'Cannot convert "1" to datetime'),
    ('invalid date', datetime.datetime, 'Cannot convert "invalid date" to datetime'),
))
def test_convert_datetime_with_errors(data, type_, expected_errors):
    with pytest.raises(ConvertException) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(('data', 'type_', 'expected_errors'), (
    (1, datetime.date, 'Cannot convert "1" to date'),
    ('invalid date', datetime.date, 'Cannot convert "invalid date" to date'),
))
def test_convert_date_with_errors(data, type_, expected_errors):
    with pytest.raises(ConvertException) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


def test_convert_without_converter():
    data = '123'
    type_ = object
    expected_errors = {'non_field_error': 'Invalid type.'}
    with pytest.raises(ConvertException) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(('data', 'type_', 'expected_errors'), (
    (1, Contact, {
        'non_field_error': 'Invalid type. Need: "object". Got: "1"',
    }),
    ({}, Contact, {
        'non_field_error': 'Missing fields: "phones"',
    }),
    (
        {
            'phones': ['invalid_integer'],
        },
        Contact,
        {
            'phones': 'Cannot convert "invalid_integer" to integer',
        }),
    (
        {
            'contact': {
                'phones': 123,
            },
        },
        User,
        {
            'non_field_error': 'Missing fields: "id", "status", "birthday", "emails"',
            'contact': {
                'phones': 'Cannot convert "123" to set',
            },
        },
    ),

))
def test_convert_dataclasss_with_errors(data, type_, expected_errors):
    with pytest.raises(ConvertException) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(('data', 'type_', 'expected_instance'), (
    ('8bd5b7f9-3cd3-4a7e-be17-23df921b7fb7', uuid.UUID, uuid.UUID('8bd5b7f9-3cd3-4a7e-be17-23df921b7fb7')),
    ('8bd5b7f9-3cd3-4a7e-be17-23df921b7fb7', Uid, Uid('8bd5b7f9-3cd3-4a7e-be17-23df921b7fb7')),
))
def test_convert_uuid(data, type_, expected_instance):
    instance = convert(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(('data', 'type_', 'expected_errors'), (
    ('invalid uuid', uuid.UUID, 'Cannot convert "invalid uuid" to uuid'),
    ('invalid uuid', Uid, 'Cannot convert "invalid uuid" to uuid'),
))
def test_convert_uuid_with_errors(data, type_, expected_errors):
    with pytest.raises(ConvertException) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(('data', 'type_', 'expected_instance'), (
    ('1.05', decimal.Decimal, decimal.Decimal('1.05')),
    (1.1, Number, Number(1.1)),
))
def test_convert_decimal(data, type_, expected_instance):
    instance = convert(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(('data', 'type_', 'expected_errors'), (
    (None, decimal.Decimal, 'Cannot convert "None" to decimal'),
    ('invalid decimal', Number, 'Cannot convert "invalid decimal" to decimal'),
))
def test_convert_decimal_with_errors(data, type_, expected_errors):
    with pytest.raises(ConvertException) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(('data', 'type_', 'expected_instance'), (
    ('1.05', decimal.Decimal, decimal.Decimal('1.05')),
    (1.1, Number, Number(1.1)),
))
def test_convert_decimal(data, type_, expected_instance):
    instance = convert(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(('data', 'type_', 'expected_errors'), (
    (None, float, 'Cannot convert "None" to float'),
    ('invalid decimal', float, 'Cannot convert "invalid decimal" to float'),
))
def test_convert_decimal_with_errors(data, type_, expected_errors):
    with pytest.raises(ConvertException) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


@pytest.mark.parametrize(('data', 'type_', 'expected_instance'), (
    ({'data': 1}, dict, {'data': 1}),
    ({'data': 1}, typing.Dict, {'data': 1}),
    ({'1': '1'}, typing.Dict[int, int], {1: 1}),
))
def test_convert_dict(data, type_, expected_instance):
    instance = convert(data, type_)
    assert instance == expected_instance


@pytest.mark.parametrize(('data', 'type_', 'expected_errors'), (
    (None, dict, 'Cannot convert "None" to object'),
    (None, typing.Dict, 'Cannot convert "None" to object'),
    ('invalid object', dict, 'Cannot convert "invalid object" to object'),
    ({'data1': 1}, typing.Dict[int, int], 'Cannot convert "data1" to integer'),
    ({1: 'data2'}, typing.Dict[float, float], 'Cannot convert "data2" to float'),
))
def test_convert_decimal_with_errors(data, type_, expected_errors):
    with pytest.raises(ConvertException) as ex:
        convert(data, type_)
    assert ex.value.errors == expected_errors


def test_convert_any():
    instance = object()
    assert convert(instance, typing.Any) is instance
