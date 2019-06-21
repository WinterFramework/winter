import pytest

from winter.pagination import Sort
from winter.pagination import Order
from winter.pagination import SortDirection


def test_empty_sort_orders():
    sort = Sort()
    assert sort.orders == ()


def test_sort_orders():
    orders = (
        Order('a', SortDirection.DESC),
        Order('b'),
    )
    sort = Sort(*orders)
    assert sort.orders == orders


def test_sort_by():
    fields = ('a', 'b')
    orders = tuple(Order(field) for field in fields)
    sort = Sort.by(*fields)
    assert sort.orders == orders


def test_sort_and():
    orders_1 = (
        Order('a', SortDirection.DESC),
        Order('b'),
    )
    orders_2 = (
        Order('c'),
        Order('d', SortDirection.ASC),
    )
    sort_1 = Sort(*orders_1)
    sort_2 = Sort(*orders_2)
    new_sort = sort_1.and_(sort_2)
    assert new_sort.orders == orders_1 + orders_2


def test_sort_asc():
    orders = (
        Order('a', SortDirection.DESC),
        Order('b', SortDirection.ASC),
        Order('c', SortDirection.DESC),
    )
    sort = Sort(*orders)
    new_sort = sort.asc()
    assert all(order.direction == SortDirection.ASC for order in new_sort.orders)


def test_sort_desc():
    orders = (
        Order('a', SortDirection.ASC),
        Order('b', SortDirection.DESC),
        Order('c', SortDirection.ASC),
    )
    sort = Sort(*orders)
    new_sort = sort.desc()
    assert all(order.direction == SortDirection.DESC for order in new_sort.orders)


def test_sort_equal():
    orders = (
        Order('a', SortDirection.DESC),
        Order('b', SortDirection.ASC),
        Order('c', SortDirection.DESC),
    )
    sort_1 = Sort(*orders)
    sort_2 = Sort(*orders)
    assert sort_1 == sort_2


def test_sort_not_equal_to_int():
    sort = Sort()
    assert sort != 0


def test_sort_hash():
    orders = (
        Order('a', SortDirection.DESC),
        Order('b', SortDirection.ASC),
        Order('c', SortDirection.DESC),
    )
    sort_1 = Sort(*orders)
    sort_2 = Sort(*orders)
    sort_3 = Sort()
    sort_set = {sort_1, sort_2, sort_3}
    assert len(sort_set) == 2


def test_sort_by_fails_for_zero_fields():
    with pytest.raises(ValueError, match='Specify at least one field.'):
        Sort.by()


def test_order_to_string():
    assert str(Order('id', SortDirection.ASC)) == 'id'
    assert str(Order('id', SortDirection.DESC)) == '-id'


def test_repr_sort():
    sort = Sort(
        Order('foo', SortDirection.ASC),
        Order('bar', SortDirection.DESC),
    )

    assert repr(sort) == "Sort('foo,-bar')"
