import importlib
import os

from injector import InstanceProvider
from injector import singleton

from winter.core import get_injector
from winter.messaging import MessagingConfig
from winter_messaging_transactional.consumer import MiddlewareCollection
from winter_messaging_transactional.messaging_app import MessagingApp


class InvalidConfiguration(Exception):
    pass


def setup():
    injector = get_injector()
    messaging_app = _get_messaging_app()
    modules_for_injector = messaging_app.get_injector_modules()
    injector.binder.install(*modules_for_injector)
    middlewares = messaging_app.get_listener_middlewares()
    injector.binder.bind(MiddlewareCollection, InstanceProvider(middlewares), scope=singleton)
    config = messaging_app.get_configuration()
    injector.binder.bind(MessagingConfig, InstanceProvider(config), scope=singleton)


def _get_messaging_app() -> MessagingApp:
    winter_settings_module = _init_winter_settings()

    messaging_app = getattr(winter_settings_module, 'messaging_app', None)
    if not isinstance(messaging_app, MessagingApp):
        raise InvalidConfiguration('worker_configuration must be instance of MessagingApp')

    return messaging_app


def _init_winter_settings():
    winter_package_name = os.environ.get('WINTER_SETTINGS_MODULE')
    if not winter_package_name:
        raise InvalidConfiguration('WINTER_SETTINGS_MODULE environment variable is not set')
    try:
        module = importlib.import_module(winter_package_name)
    except ModuleNotFoundError as e:
        message = f'"{winter_package_name}" module could not be imported. {e}'
        raise InvalidConfiguration(message)
    return module
