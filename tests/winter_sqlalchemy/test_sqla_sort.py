import pytest
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import select

from winter.data.pagination import Sort
from winter_sqlalchemy import sort


@pytest.mark.parametrize(
    'sort_, expected_ids', [
        (Sort.by('id'), [1, 2, 3]),
        (Sort.by('id').desc(), [3, 2, 1]),
    ],
)
def test_sort(id_database, sort_, expected_ids):
    engine, table = id_database
    statement = sort(select([table.c.id]), sort_)
    result = engine.execute(statement)
    ids = [row[0] for row in result]

    assert ids == expected_ids


@pytest.fixture(scope='module')
def id_database():
    engine = create_engine('sqlite://')
    metadata = MetaData(engine)
    table = Table('table', metadata, Column('id', Integer, primary_key=True))
    metadata.create_all()
    rows = [{'id': value} for value in range(1, 4)]
    engine.execute(table.insert(), *rows)
    return engine, table
