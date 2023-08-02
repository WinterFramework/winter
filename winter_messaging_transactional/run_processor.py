import os

from winter_messaging_transactional.startup_teardown import process_start
from winter_messaging_transactional.startup_teardown import process_stop
from .producer.publish_processor import PublishProcessor
from winter.core import get_injector
from .setup import setup

if os.getenv('USE_COVERAGE', 'false').lower() == 'true':  # pragma: no cover
    # noinspection PyUnresolvedReferences
    import winter_messaging_transactional.tests.coverage  # noqa: F401, F403


if __name__ == '__main__':
    process_start()
    try:
        setup()
        injector = get_injector()
        processor = injector.get(PublishProcessor)
        processor.run()
    finally:
        process_stop()

