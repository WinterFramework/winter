import importlib
import inspect
import os

from injector import Injector
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from winter.core import set_injector
from .injection_modules import TransactionalMessagingModule
from .messaging_app import MessagingApp
from .table_metadata import messaging_metadata


class InvalidConfiguration(Exception):
    pass


def setup():
    injector = Injector([])
    set_injector(injector)
    messaging_app = _create_messaging_app()
    injector.binder.install(TransactionalMessagingModule)
    messaging_app.setup(injector)
    engine = injector.get(Engine)
    messaging_metadata.create_all(engine)


def _create_messaging_app() -> MessagingApp:
    winter_settings_module = _init_winter_settings()

    messaging_app_class = None
    for class_name, class_ in inspect.getmembers(winter_settings_module, inspect.isclass):
        if issubclass(class_, MessagingApp) and class_ is not MessagingApp:
            messaging_app_class = class_
            break

    if not messaging_app_class:
        raise InvalidConfiguration('Define subclass of MessagingApp and override setup method')

    return messaging_app_class()


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
