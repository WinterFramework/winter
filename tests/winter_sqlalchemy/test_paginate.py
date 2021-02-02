import pytest
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import select

from winter.data.pagination import PagePosition
from winter.data.pagination import Sort
from winter_sqlalchemy import paginate


@pytest.mark.parametrize(
    'limit, offset, sort, expected_ids', [
        (None, None, None, None),
        (None, None, Sort.by('id'), [1, 2, 3, 4, 5]),
        (None, None, Sort.by('id').desc(), [5, 4, 3, 2, 1]),
        (3, None, Sort.by('id'), [1, 2, 3]),
        (6, None, Sort.by('id'), [1, 2, 3, 4, 5]),
        (2, 2, Sort.by('id'), [3, 4]),
        (None, 2, Sort.by('id'), [3, 4, 5]),
    ],
)
def test_paginate(id_database, limit, offset, sort, expected_ids):
    engine, table = id_database
    statement = paginate(select([table.c.id]), PagePosition(limit, offset, sort))
    result = engine.execute(statement)
    ids = [row[0] for row in result]
    if expected_ids is None:
        assert len(ids) == 5
    else:
        assert ids == expected_ids


@pytest.fixture(scope='module')
def id_database():
    engine = create_engine('sqlite://')
    metadata = MetaData(engine)
    table = Table('table', metadata, Column('id', Integer, primary_key=True))
    metadata.create_all()
    rows = [{'id': value} for value in range(1, 6)]
    engine.execute(table.insert(), *rows)
    return engine, table
