from typing import List

from injector import ClassProvider
from injector import Module
from injector import singleton

from winter.messaging import EventHandlerRegistry
from winter.messaging import EventPublisher
from winter.messaging import MessagingConfig
from winter_messaging_transactional.consumer import MiddlewareClass
from winter_messaging_transactional.messaging_app import MessagingApp
from winter_messaging_transactional.producer.outbox import OutboxEventPublisher


class TestAppModule(Module):
    def configure(self, binder):
        binder.bind(EventPublisher, to=ClassProvider(OutboxEventPublisher))


class TestMessagingApp(MessagingApp):

    def get_injector_modules(self) -> List[Module]:
        return [TestAppModule()]

    def get_listener_middlewares(self) -> List[MiddlewareClass]:
        return []

    def get_configuration(self) -> MessagingConfig:
        return MessagingConfig(
            topics={'sample-producer-topic'},
            consumers={
                'consumer_correct': {'tests.winter_messaging.app_sample.consumer_correct'},
                'consumer_slow': {'tests.winter_messaging.app_sample.consumer_slow'},
                'consumer_with_bug': {'tests.winter_messaging.app_sample.consumer_with_bug'},
            }
        )


messaging_app = TestMessagingApp()
