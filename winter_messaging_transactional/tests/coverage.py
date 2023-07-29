from pathlib import Path

import coverage

from winter_messaging_transactional.startup_teardown import on_process_start
from winter_messaging_transactional.startup_teardown import on_process_stop

ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_FILE = ROOT_DIR / '.coveragerc'


def get_coverage(label: str) -> coverage.Coverage:
    data_file = ROOT_DIR / 'test_coverage' / f'.coverage.{label}'
    return coverage.Coverage(config_file=str(CONFIG_FILE), data_file=str(data_file))


cov = get_coverage('winter_messaging_transactional')


@on_process_start
def start_coverage():
    cov.start()


@on_process_stop
def stop_coverage():
    cov.stop()
    cov.save()
