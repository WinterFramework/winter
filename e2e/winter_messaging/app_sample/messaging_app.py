import os
from injector import ClassProvider, Injector
from injector import InstanceProvider
from injector import singleton
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine

from e2e.winter_messaging.app_sample.dao.consumer_dao import messaging_app_metadata
from winter.messaging import EventPublisher
from winter.messaging import MessagingConfig
from winter_messaging_transactional.messaging_app import MessagingApp
from winter_messaging_transactional.producer.outbox import OutboxEventPublisher


class WinterMessagingApp(MessagingApp):

    def setup(self, injector: Injector):
        injector.binder.bind(EventPublisher, to=ClassProvider(OutboxEventPublisher))
        config = MessagingConfig(
            topics={'sample-topic'},
            consumers={
                'consumer_correct': {'e2e.winter_messaging.app_sample.consumer_correct'},
                'consumer_timeout': {'e2e.winter_messaging.app_sample.consumer_timeout'},
                'consumer_with_error': {'e2e.winter_messaging.app_sample.consumer_with_error'},
            }
        )
        injector.binder.bind(MessagingConfig, to=InstanceProvider(config), scope=singleton)
        engine = make_engine()
        injector.binder.bind(Engine, to=engine, scope=singleton)
        messaging_app_metadata.create_all(engine)


def make_engine():
    database_url = os.getenv('WINTER_DATABASE_URL')
    return create_engine(database_url)
