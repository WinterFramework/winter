import argparse
import importlib
import logging
import sys
import django
import winter.core
import winter_django

from injector import Injector

from winter_messaging_outbox_transacton.consumer_worker import ConsumerWorker

from winter_messaging_outbox_transacton.injector_config import MessagingConfiguration
from winter_messaging_outbox_transacton.middleware_registry import MiddlewareRegistry
from winter_messaging_outbox_transacton.worker_configuration import get_worker_configuration

logger = logging.getLogger(__name__)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def parse_args(parser_object):
    parser_object.add_argument(
        'consumer',
        type=str,
        help='Consumer ID',
    )
    parser_object.add_argument(
        '-p',
        '--package-module',
        type=str,
        dest='package_module',
        help='',
    )
    return parser_object.parse_args()


if __name__ == '__main__':
    parser = Parser(description='Run consumer worker')
    args = parse_args(parser)

    consumer_id = args.consumer
    package_name = args.package_module
    injector = Injector([MessagingConfiguration()])
    winter.core.set_injector(injector)
    try:
        worker_module = importlib.import_module(f'{package_name}.worker')
    except ModuleNotFoundError:
        worker_module = None

    winter_django.setup()
    django.setup()

    middlewares = []
    worker_configuration = get_worker_configuration(package_name)
    if worker_configuration:
        modules_for_injector = worker_configuration.get_modules_for_injector()
        injector_modules = [*modules_for_injector]
        middlewares = worker_configuration.get_middlewares()
        injector.binder.install(*injector_modules)

    middleware_registry = MiddlewareRegistry(middlewares)
    worker = injector.get(ConsumerWorker)

    logger.info(f'Starting message consumer id: %s; in package: %s', consumer_id, package_name)
    worker.start(consumer_id=consumer_id)
