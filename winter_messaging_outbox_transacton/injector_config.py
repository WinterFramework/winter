from injector import CallableProvider
from injector import ClassProvider
from injector import Module
from injector import singleton
from pika import BlockingConnection

from winter.messaging import EventHandlerRegistry
from winter_messaging_outbox_transacton.consumer_worker import ConsumerWorker
from winter_messaging_outbox_transacton.outbox import OutboxMessageDAO
from winter_messaging_outbox_transacton.rabbitmq import TopologyConfigurator
from winter_messaging_outbox_transacton.rabbitmq import create_connection


class MessagingConfiguration(Module):
    def configure(self, binder):
        binder.bind(ConsumerWorker, to=ClassProvider(ConsumerWorker), scope=singleton)
        binder.bind(EventHandlerRegistry, to=ClassProvider(EventHandlerRegistry), scope=singleton)
        binder.bind(TopologyConfigurator, to=ClassProvider(TopologyConfigurator), scope=singleton)
        binder.bind(BlockingConnection, to=CallableProvider(create_connection), scope=singleton)
        binder.bind(OutboxMessageDAO, to=ClassProvider(OutboxMessageDAO))
