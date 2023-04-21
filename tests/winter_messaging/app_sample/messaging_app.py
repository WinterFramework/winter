from injector import ClassProvider
from injector import InstanceProvider
from injector import singleton

from winter.messaging import EventPublisher
from winter.messaging import MessagingConfig
from winter_messaging_transactional.messaging_app import MessagingApp
from winter_messaging_transactional.producer.outbox import OutboxEventPublisher


class TestMessagingApp(MessagingApp):

    def setup(self, injector):
        injector.binder.bind(EventPublisher, to=ClassProvider(OutboxEventPublisher))
        config = MessagingConfig(
            topics={'sample-producer-topic'},
            consumers={
                'consumer_correct': {'tests.winter_messaging.app_sample.consumer_correct'},
                'consumer_slow': {'tests.winter_messaging.app_sample.consumer_slow'},
                'consumer_with_bug': {'tests.winter_messaging.app_sample.consumer_with_bug'},
            }
        )
        injector.binder.bind(MessagingConfig, to=InstanceProvider(config), scope=singleton)


messaging_app = TestMessagingApp()
