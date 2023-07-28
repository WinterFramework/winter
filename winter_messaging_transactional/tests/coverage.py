from pathlib import Path

import coverage

ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_FILE = ROOT_DIR / '.coveragerc'


def get_coverage(label: str) -> coverage.Coverage:
    data_file = ROOT_DIR / 'test_coverage' / f'.coverage.{label}'
    return coverage.Coverage(config_file=str(CONFIG_FILE), data_file=str(data_file))
