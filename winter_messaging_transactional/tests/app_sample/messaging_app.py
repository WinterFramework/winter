import logging
import os
import sys

from injector import CallableProvider
from injector import ClassProvider, Injector
from injector import InstanceProvider
from injector import singleton
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from winter_messaging_transactional.consumer import MiddlewareCollection
from winter_messaging_transactional.consumer.middleware_registry import Middleware
from winter_messaging_transactional.tests.app_sample.dao.consumer_dao import messaging_app_metadata
from winter.messaging import EventPublisher
from winter.messaging import MessagingConfig
from winter_messaging_transactional.messaging_app import MessagingApp
from winter_messaging_transactional.producer.outbox import OutboxEventPublisher

logger = logging.getLogger('test')


class WinterMessagingApp(MessagingApp):

    def setup(self, injector: Injector):
        injector.binder.bind(EventPublisher, to=ClassProvider(OutboxEventPublisher))
        config = MessagingConfig(
            topics={'sample-topic'},
            consumers={
                'consumer_correct': {'winter_messaging_transactional.tests.app_sample.consumer_correct'},
                'consumer_timeout': {'winter_messaging_transactional.tests.app_sample.consumer_timeout'},
                'consumer_with_error': {'winter_messaging_transactional.tests.app_sample.consumer_with_error'},
            }
        )
        injector.binder.bind(MessagingConfig, to=InstanceProvider(config), scope=singleton)
        injector.binder.bind(MiddlewareCollection, to=InstanceProvider([AppMiddleware]))

        engine = make_engine()
        messaging_app_metadata.create_all(engine)

        session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=True)
        ScopedSession = scoped_session(session_factory)

        injector.binder.bind(Engine, to=engine, scope=singleton)
        injector.binder.bind(Session, to=CallableProvider(ScopedSession))

        logging.basicConfig(stream=sys.stdout, level=logging.WARNING)


def make_engine():
    database_url = os.getenv('WINTER_DATABASE_URL')
    return create_engine(database_url)


class AppMiddleware(Middleware):
    def __call__(self):
        logger.info('start event handling')
        self._next()
        logger.info('finish event handling')

