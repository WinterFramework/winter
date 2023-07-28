import time
from contextlib import contextmanager

import pytest
from injector import Injector
from injector import singleton
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from testcontainers.rabbitmq import RabbitMqContainer

from winter_messaging_transactional.tests.database_container import database_container
from winter_messaging_transactional.tests.helpers import run_consumer
from winter_messaging_transactional.tests.helpers import run_processor
from winter_messaging_transactional.injection_modules import TransactionalMessagingModule
from winter_messaging_transactional.table_metadata import messaging_metadata


@pytest.fixture
def injector(session):
    injector = Injector([TransactionalMessagingModule()])
    injector.binder.bind(Engine, to=db_engine, scope=singleton)
    injector.binder.bind(Session, to=session, scope=singleton)
    return injector


@pytest.fixture
def session(db_engine):
    session_factory = sessionmaker(bind=db_engine, autoflush=False)
    session = session_factory()
    yield session
    session.close()


@pytest.fixture
def db_engine(database_url):
    engine = create_engine(database_url)
    messaging_metadata.drop_all(engine)
    messaging_metadata.create_all(engine)
    return engine


@pytest.fixture
def database_url(request):
    database_name = request.node.name.replace('[', '').replace(']', '').lower()
    return database_container.create_database(database_name)


@pytest.fixture
def rabbit_url():
    with RabbitMqContainer("rabbitmq:3.11.5") as rabbitmq:
        params = rabbitmq.get_connection_params()
        rabbit_url = f'amqp://{params.credentials.username}:{params.credentials.username}@{params.host}:{params.port}/'
        yield rabbit_url


@pytest.fixture
def event_processor(database_url: str, rabbit_url: str, db_engine):
    process = run_processor(database_url, rabbit_url)
    time.sleep(2)
    yield process
    process.terminate()
    print(process.stderr.read1().decode('utf-8'))
    print(process.stdout.read1().decode('utf-8'))


@contextmanager
def event_consumer(database_url: str, rabbit_url: str, consumber_id: str):
    process = run_consumer(database_url=database_url, rabbit_url=rabbit_url, consumer_id=consumber_id)
    yield process
    process.terminate()
    time.sleep(40)
    print(process.stderr.read1().decode('utf-8'))
    print(process.stdout.read1().decode('utf-8'))


