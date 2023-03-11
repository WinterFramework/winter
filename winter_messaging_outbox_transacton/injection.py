from injector import CallableProvider
from injector import ClassProvider
from injector import Module
from injector import singleton
from pika.adapters.blocking_connection import BlockingChannel
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from winter.messaging import EventHandlerRegistry
from winter_messaging_outbox_transacton.middleware_registry import MiddlewareRegistry

from winter_messaging_outbox_transacton.rabbitmq import connect_to_rabbit


def make_engine():
    return create_engine('postgresql+psycopg2://supplyshift:supplyshift@localhost/winter')


class Configuration(Module):
    def configure(self, binder):
        binder.bind(Engine, to=CallableProvider(make_engine), scope=singleton)
        binder.bind(BlockingChannel, to=CallableProvider(connect_to_rabbit), scope=singleton)
        binder.bind(EventHandlerRegistry, to=ClassProvider(EventHandlerRegistry), scope=singleton)
        binder.bind(MiddlewareRegistry, to=ClassProvider(MiddlewareRegistry), scope=singleton)
