from typing import Iterable
from typing import List
from typing import Optional
from typing import TypeVar

from injector import inject
from sqlalchemy import and_
from sqlalchemy import exists
from sqlalchemy import func
from sqlalchemy import inspect
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import UnmappedClassError

from winter.data import CRUDRepository
from winter.data.exceptions import NotFoundException
from winter_ddd import AggregateRoot
from winter_ddd import DomainEvent
from winter_ddd import global_domain_event_dispatcher

T = TypeVar('T')
K = TypeVar('K')


def sqla_crud(repository_cls):
    if not issubclass(repository_cls, CRUDRepository):
        raise TypeError('Repository must be inherited from CRUDRepository before annotating with sqla_crud')

    entity_cls = repository_cls.__entity_cls__

    if not issubclass(entity_cls, AggregateRoot):
        raise TypeError('Entity class must be inherited from winter_ddd.AggregateRoot')

    try:
        mapper = class_mapper(entity_cls)
    except UnmappedClassError:
        raise TypeError('Invalid SQLAlchemy entity class given')

    if len(mapper.tables) > 1:
        raise TypeError('sqla_crud does not support entities mapped to multiple tables')

    entity_table = mapper.tables[0]

    class RepositoryImpl(repository_cls):
        """
        SQLAlchemy implementation for CRUDRepository
        This repository implementation is not thread-safe.
        """
        class RepositoryException(Exception):
            pass

        def count(self) -> int:
            return self._engine.execute(select([func.count()]).select_from(entity_table)).scalar()

        def delete(self, entity: T):
            try:
                session = self._sessions[entity]
            except KeyError:
                raise self.RepositoryException('Entity must be fetched with repository before being deleted')
            pk = inspect(entity).identity
            del self._identity_map[pk]
            session.delete(entity)
            session.commit()
            session.close()
            del self._sessions[entity]

        def delete_many(self, entities: Iterable[T]):
            for entity in entities:
                self.delete(entity)

        def delete_all(self):
            self._engine.execute(entity_table.delete())
            self._identity_map = {}
            for session in self._sessions.values():
                session.close()
            self._sessions = {}

        def delete_by_id(self, id_: K):
            if not isinstance(id_, tuple):
                id_ = (id_,)
            if id_ in self._identity_map:
                entity = self._identity_map[id_]
                self.delete(entity)
            else:
                expressions = (column == value for column, value in zip(entity_table.primary_key.columns, id_))
                self._engine.execute(entity_table.delete().where(and_(*expressions)))

        def exists_by_id(self, id_: K) -> bool:
            if not isinstance(id_, tuple):
                id_ = (id_,)
            if id_ in self._identity_map:
                return True
            expressions = (column == value for column, value in zip(entity_table.primary_key.columns, id_))
            return self._engine.execute(select([exists().where(and_(*expressions))])).scalar()

        def find_all(self) -> Iterable[T]:
            ids = self._engine.execute(select(entity_table.primary_key.columns))
            ids = next(zip(*ids))
            return self.find_all_by_id(ids)

        def find_all_by_id(self, ids: Iterable[K]) -> Iterable[T]:
            result = [self.find_by_id(id_) for id_ in ids]
            result = [entity for entity in result if entity]
            return result

        def find_by_id(self, id_: K) -> Optional[T]:
            if not isinstance(id_, tuple):
                id_ = (id_,)
            if id_ in self._identity_map:
                return self._identity_map[id_]

            session = self._session_factory()
            instance = session.query(entity_cls).get(id_)
            if instance is None:
                return None

            self._identity_map[id_] = instance
            self._sessions[instance] = session
            return instance

        def get_by_id(self, id_: K) -> T:
            entity = self.find_by_id(id_)
            if entity is None:
                raise NotFoundException(id_, entity_cls)
            return entity

        def save(self, entity: T) -> T:
            self._save(entity)
            self._process_domain_events([entity])
            return entity

        def save_many(self, entities: Iterable[T]) -> Iterable[T]:
            entities = list(entities)
            for entity in entities:
                self._save(entity)
            self._process_domain_events(entities)
            return entities

        def _save(self, entity: T):
            if entity not in self._sessions:
                self._sessions[entity] = self._session_factory()
                self._sessions[entity].add(entity)
            self._sessions[entity].flush()
            pk = inspect(entity).identity
            self._identity_map[pk] = entity

        def _process_domain_events(self, aggregates: Iterable[AggregateRoot]):
            domain_events: List[DomainEvent] = []
            for aggregate in aggregates:
                domain_events.extend(aggregate.domain_events)
                aggregate.clear_domain_events()
            global_domain_event_dispatcher.dispatch(domain_events)

        @inject
        def __init__(self, engine: Engine):
            self._engine = engine
            self._session_factory = sessionmaker(bind=self._engine)
            self._identity_map = {}
            self._sessions = {}

    # def func1(self, name, lastname):
    #     return self._session_factory().query(entity_cls).filter(
    #         getattr(entity_cls, 'name') == name,
    #         getattr(entity_cls, 'lastname') == lastname,
    #     ).one_or_none()
    #
    # RepositoryImpl.find_one_by_name_and_lastname = func1

    return RepositoryImpl
