import os

from injector import Injector
from injector import InstanceProvider
from injector import singleton
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from winter.messaging import MessagingConfig
from winter_messaging_transactional import MessagingApp


class WinterMessagingApp(MessagingApp):

    def setup(self, injector: Injector):
        config = MessagingConfig(
            topics={'test-topic'},
            consumers={
                'consumer': {'winter_messaging_transactional.tests.incorrect_app_sample.simple_event_handler'},
            }
        )
        injector.binder.bind(MessagingConfig, to=InstanceProvider(config), scope=singleton)

        database_url = os.getenv('WINTER_DATABASE_URL')
        engine = create_engine(database_url)
        injector.binder.bind(Engine, to=engine, scope=singleton)
