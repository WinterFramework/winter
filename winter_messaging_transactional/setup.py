import importlib
import os

from winter.core import get_injector
from .injection_modules import TransactionalMessagingModule
from .messaging_app import MessagingApp


class InvalidConfiguration(Exception):
    pass


def setup():
    injector = get_injector()
    messaging_app = _get_messaging_app()
    messaging_app.setup(injector)
    injector.binder.install(TransactionalMessagingModule)


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
