import argparse
import os
import sys

from winter_messaging_transactional.producer.outbox_cleanup_processor import OutboxCleanupProcessor
from winter_messaging_transactional.startup_teardown import process_start
from winter_messaging_transactional.startup_teardown import process_stop
from winter.core import get_injector
from .setup import setup

if os.getenv('USE_COVERAGE', 'false').lower() == 'true':  # pragma: no cover
    # noinspection PyUnresolvedReferences
    import winter_messaging_transactional.tests.coverage  # noqa: F401, F403


class Parser(argparse.ArgumentParser):
    def error(self, message):  # pragma: no cover
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def parse_args(parser_object):
    parser_object.add_argument(
        '--interval',
        dest='interval',
        default=15,
        type=int,
        help='Cleanup interval',
    )
    return parser_object.parse_args()


if __name__ == '__main__':
    process_start()

    parser = Parser(description='Run outbox cleanup processor')
    args = parse_args(parser)
    cleanup_interval = float(args.interval)

    try:
        setup()
        injector = get_injector()
        processor = injector.get(OutboxCleanupProcessor)
        processor.run(cleanup_interval=cleanup_interval)
    finally:
        process_stop()
