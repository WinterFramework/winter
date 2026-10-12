"""The codemod runs as a script; these tests drive it the way a consumer does, through the CLI."""
import pathlib
import subprocess
import sys

import pytest

CODEMOD = pathlib.Path(__file__).parents[2] / 'tools' / 'migrate_to_33.py'


def _migrate(tmp_path: pathlib.Path, source: str) -> str:
    target = tmp_path / 'module.py'
    target.write_text(source)
    subprocess.run([sys.executable, str(CODEMOD), str(target)], check=True, capture_output=True)
    return target.read_text()


@pytest.mark.parametrize('source, expected', [
    (
        'import winter\n\n@winter.route_get("x/")\ndef f(): ...\n',
        'import winter.web\n\n@winter.web.route_get("x/")\ndef f(): ...\n',
    ),
    (
        'from winter_django import create_django_urls\nfrom winter.core import get_injector\n\n'
        'urls = create_django_urls(get_injector())\n',
        'from winter.django import create_django_urls\nfrom winter.application import get_injector\n\n'
        'urls = create_django_urls(get_injector())\n',
    ),
    (
        'from winter.web.routing import reverse\n\nurl = reverse(f)\n',
        'from winter.django import reverse\n\nurl = reverse(f)\n',
    ),
    (
        'from winter.web.throttling import RedisThrottlingConfiguration\n'
        'from winter.web.throttling import set_redis_throttling_configuration\n\n'
        'set_redis_throttling_configuration(RedisThrottlingConfiguration(host="h", port=1, db=0))\n',
        'from winter.redis.throttling import RedisThrottlingConfiguration\n'
        'from winter.redis.throttling import RedisThrottlingStorage\n'
        'from winter.web import set_throttling_storage\n\n'
        'set_throttling_storage(RedisThrottlingStorage(RedisThrottlingConfiguration(host="h", port=1, db=0)))\n',
    ),
    (
        'import winter.web\n\nwinter.web.set_redis_throttling_configuration(config)\n',
        'import winter.web\n'
        'from winter.redis.throttling import RedisThrottlingStorage\n'
        'from winter.web import set_throttling_storage\n\n'
        'set_throttling_storage(RedisThrottlingStorage(config))\n',
    ),
])
def test_migrate(tmp_path, source, expected):
    assert _migrate(tmp_path, source) == expected


def test_migration_is_idempotent(tmp_path):
    source = 'from winter.web import route_get\nfrom winter.redis.throttling import RedisThrottlingStorage\n'
    assert _migrate(tmp_path, source) == source


def test_check_mode_reports_without_writing(tmp_path):
    target = tmp_path / 'module.py'
    target.write_text('import winter_ddd\n')

    result = subprocess.run([sys.executable, str(CODEMOD), '--check', str(target)], capture_output=True, text=True)

    assert result.returncode == 1
    assert result.stdout.strip() == str(target)
    assert target.read_text() == 'import winter_ddd\n'
