from abc import ABCMeta
from abc import abstractmethod
from typing import Optional

import pytest
import sqlalchemy as sa
from dataclasses import dataclass
from injector import ClassProvider
from injector import inject
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.engine import Engine
from sqlalchemy.orm import mapper

from winter.core import get_injector
from winter.data import CRUDRepository
from winter.data.exceptions import NotFoundException
from winter_ddd import AggregateRoot
from winter_ddd import DomainEvent
from winter_ddd import domain_event_handler
from winter_sqlalchemy import sqla_crud


@dataclass
class MarkedAsDoneDomainEvent(DomainEvent):
    entity: 'MyEntity'


class MyEntity(AggregateRoot):
    def __init__(self, id_: int, name: Optional[str], lastname: Optional[str]):
        super().__init__()
        self.id = id_
        self.name = name
        self.lastname = lastname

    def mark_as_done(self):
        self.name = 'done'
        self.domain_events.register(MarkedAsDoneDomainEvent(self))


metadata = MetaData()
my_entity_table = Table(
    'my_entities',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('lastname', String),
)
mapper(MyEntity, my_entity_table)


class MyRepository(CRUDRepository[MyEntity, int]):
    @abstractmethod
    def find_one_by_name_and_lastname(self, name: str, lastname: str) -> Optional[MyEntity]:
        pass


class MyRepositoryImpl(MyRepository, metaclass=ABCMeta):
    @inject
    def __init__(self, engine: Engine):
        self._engine = engine

    def find_one_by_name_and_lastname(self, name: str, lastname: str) -> Optional[MyEntity]:
        query = sa.select([
            my_entity_table.c.id,
        ]).where(
            sa.and_(my_entity_table.c.name == name, my_entity_table.c.lastname == lastname),
        )
        with self._engine.connect() as connection:
            rows = connection.execute(query)
        rows = list(rows)
        assert len(rows) <= 1
        if not rows:
            return None
        entity_id = rows[0][0]
        return self.get_by_id(entity_id)


class DomainEventHandlers:
    @inject
    def __init__(self, repository: MyRepository):
        self._repository = repository

    @domain_event_handler
    def on_marked_as_done(self, event: MarkedAsDoneDomainEvent):
        entity = event.entity
        new_entity = MyEntity(
            id_=entity.id * 100,
            name='handled',
            lastname='',
        )
        self._repository.save(new_entity)


@pytest.fixture()
def fixture():
    return get_injector().get(Fixture)


@pytest.fixture()
def engine():
    return get_injector().get(Engine)


class Fixture:
    @inject
    def __init__(self, engine: Engine):
        injector = get_injector()
        injector.binder.bind(MyRepository, to=ClassProvider(sqla_crud(MyRepository)))
        self._engine = engine
        self.repository = injector.get(MyRepository)
        metadata.drop_all(bind=self._engine)
        metadata.create_all(bind=self._engine)

    def execute(self, sql):
        return self._engine.execute(sql)


def test_count(fixture):
    fixture.execute('INSERT INTO my_entities (id) VALUES (1), (2), (3);')

    # Act
    count = fixture.repository.count()

    assert count == 3


def test_delete(fixture):
    fixture.execute('INSERT INTO my_entities (id) VALUES (1), (2);')
    entity = fixture.repository.find_by_id(1)

    # Act
    fixture.repository.delete(entity)

    result = fixture.execute('SELECT id FROM my_entities;')
    assert list(result) == [(2,)]
    assert fixture.repository.find_by_id(1) is None


def test_delete_many(fixture):
    fixture.execute('INSERT INTO my_entities (id) VALUES (1), (2), (3);')
    entity_1 = fixture.repository.find_by_id(1)
    entity_3 = fixture.repository.find_by_id(3)

    # Act
    fixture.repository.delete_many([entity_1, entity_3])

    result = fixture.execute('SELECT id FROM my_entities;')
    assert list(result) == [(2,)]
    assert fixture.repository.find_by_id(1) is None
    assert fixture.repository.find_by_id(3) is None


def test_delete_all(fixture):
    fixture.execute('INSERT INTO my_entities (id) VALUES (1), (2), (3);')

    # Act
    fixture.repository.delete_all()

    count = fixture.execute('SELECT COUNT(*) FROM my_entities;').scalar()
    assert count == 0


def test_delete_by_id(fixture):
    fixture.execute('INSERT INTO my_entities (id) VALUES (1), (2);')

    # Act
    fixture.repository.delete_by_id(1)

    result = fixture.execute('SELECT id FROM my_entities;')
    assert list(result) == [(2,)]


def test_exists_by_id(fixture):
    fixture.execute('INSERT INTO my_entities (id) VALUES (1), (2);')

    # Act
    exists = fixture.repository.exists_by_id(2)

    assert exists is True


def test_not_exists_by_id(fixture):
    fixture.execute('INSERT INTO my_entities (id) VALUES (1), (2);')

    # Act
    exists = fixture.repository.exists_by_id(3)

    assert exists is False


def test_find_all(fixture):
    fixture.execute('INSERT INTO my_entities (id) VALUES (1), (2), (3);')

    # Act
    entities = fixture.repository.find_all()

    ids = [entity.id for entity in entities]
    assert len(ids) == 3
    assert set(ids) == {1, 2, 3}


def test_find_all_by_id(fixture):
    fixture.execute('INSERT INTO my_entities (id) VALUES (1), (2), (3);')

    # Act
    entities = fixture.repository.find_all_by_id([1, 4, 3])

    ids = [entity.id for entity in entities]
    assert len(ids) == 2
    assert set(ids) == {1, 3}


def test_find_by_id(fixture):
    fixture.execute('INSERT INTO my_entities (id) VALUES (1), (2), (3);')

    # Act
    entity = fixture.repository.find_by_id(2)

    assert entity.id == 2


def test_get_by_id(fixture):
    with pytest.raises(NotFoundException, match='MyEntity with ID=2 not found'):
        # Act
        fixture.repository.get_by_id(2)


def test_save_new(fixture):
    entity = MyEntity(id_=1, name='name', lastname='lastname')

    # Act
    entity = fixture.repository.save(entity)

    entities = list(fixture.repository.find_all())
    assert len(entities) == 1
    assert entities[0].id == 1
    assert entities[0].name == 'name'
    assert entities[0].lastname == 'lastname'


def test_save(fixture):
    fixture.execute("INSERT INTO my_entities (id, name) VALUES (1, 'started'), (2, 'started'), (3, 'started');")
    entity = fixture.repository.find_by_id(2)
    entity.mark_as_done()

    # Act
    entity = fixture.repository.save(entity)

    assert entity.name == 'done'
    entities = fixture.execute('SELECT id, name FROM my_entities;').fetchall()
    entities = [(id_, name) for id_, name in entities]
    assert len(entities) == 4
    assert set(entities) == {(1, 'started'), (2, 'done'), (3, 'started'), (200, 'handled')}


def test_save_many(fixture):
    fixture.execute("INSERT INTO my_entities (id, name) VALUES (1, 'started'), (2, 'started'), (3, 'started');")
    entities = fixture.repository.find_all_by_id([1, 3])
    for entity in entities:
        entity.mark_as_done()

    # Act
    entities = fixture.repository.save_many(entities)

    entities = list(entities)
    assert len(entities) == 2
    assert all(entity.name == 'done' for entity in entities)
    entities = fixture.execute('SELECT id, name FROM my_entities;').fetchall()
    entities = [(id_, name) for id_, name in entities]
    assert len(entities) == 5
    assert set(entities) == {(1, 'done'), (2, 'started'), (3, 'done'), (100, 'handled'), (300, 'handled')}


@pytest.mark.parametrize(
    'name, lastname, entity_id', [
        ('name', 'something', None),
        ('name', 'lastname', 2),
    ],
)
def test_find_one_by_name_and_lastname(fixture, name, lastname, entity_id):
    fixture.execute("INSERT INTO my_entities (id, name, lastname) VALUES (1, 'name', NULL), (2, 'name', 'lastname');")

    # Act
    entity = fixture.repository.find_one_by_name_and_lastname(name, lastname)

    if entity_id is None:
        assert entity is None
    else:
        assert entity.id == entity_id
