import argparse
import importlib
import signal
import sys

from injector import Injector

from winter_messaging_outbox_transacton.consumer_worker import ConsumerWorker
from winter_messaging_outbox_transacton.exceptions import InterruptProcessException
from winter_messaging_outbox_transacton.injection import Configuration


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
    import django
    import winter.core
    import winter_django

    parser = Parser(description='Run consumer worker')
    args = parse_args(parser)

    consumer_id = args.consumer
    package_name = args.package_module

    worker_module = importlib.import_module(f'{package_name}.worker')

    winter_django.setup()
    django.setup()

    modules_for_injector = worker_module.worker_configuration.get_modules_for_injector()
    injector_modules = [*modules_for_injector, Configuration()]

    injector = Injector(injector_modules)
    winter.core.set_injector(injector)

    worker = injector.get(ConsumerWorker)


    def stop_worker(signum, frame):
        worker.stop()
        raise InterruptProcessException()

    signal.signal(signal.SIGTERM, stop_worker)
    signal.signal(signal.SIGINT, stop_worker)

    print(f'Starting message consumer id: {consumer_id}; in package: {package_name}')
    worker.start(consumer_id=consumer_id, package_name=package_name)
