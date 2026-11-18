from injector import CallableProvider
from injector import Injector
from injector import Module
from injector import singleton
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from winter.web import InMemoryThrottlingStorage
from winter.web import ThrottlingStorage


class Configuration(Module):
    def configure(self, binder):
        binder.bind(Engine, to=CallableProvider(make_engine), scope=singleton)
        # The Redis storage is covered in tests/redis; the sample application throttles in memory
        binder.bind(ThrottlingStorage, to=InMemoryThrottlingStorage, scope=singleton)


def make_engine():
    return create_engine('sqlite://')


# The injector of the sample application in tests/urls.py, which the tests share
app_injector = Injector([Configuration])
