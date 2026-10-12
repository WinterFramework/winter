"""tools/migrate_to_33.py is a script, not a package; the tests load it from its path and drive `main`."""
import importlib.util
import pathlib

import pytest

CODEMOD = pathlib.Path(__file__).parents[2] / 'tools' / 'migrate_to_33.py'
_spec = importlib.util.spec_from_file_location('migrate_to_33', CODEMOD)
migrate_to_33 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migrate_to_33)


def _migrate(tmp_path: pathlib.Path, source: str) -> str:
    target = tmp_path / 'module.py'
    target.write_text(source)
    migrate_to_33.main([str(target)])
    return target.read_text()


@pytest.mark.parametrize('source, expected', [
    (
        'import os\nimport winter\n\n\n@winter.route_get("x/")\ndef f():\n    return os.getcwd()\n',
        'import os\nimport winter.web\n\n\n@winter.web.route_get("x/")\ndef f():\n    return os.getcwd()\n',
    ),
    (
        'import winter\n\nname = winter.__name__\n',
        'import winter\n\nname = winter.__name__\n',
    ),
    (
        'import winter\nimport winter.web\n\nx = winter.web.route_get\n',
        'import winter.web\n\nx = winter.web.route_get\n',
    ),
    (
        'from winter_django import create_django_urls\nfrom winter.core import get_injector\n\n'
        'urls = create_django_urls(get_injector())\n',
        'from winter.django import create_django_urls\nfrom winter.application import get_injector\n\n'
        'urls = create_django_urls(get_injector())\n',
    ),
    (
        'from winter.core.utils.typing import is_optional\n\nimport winter\n\nx = winter.ResponseEntity\n',
        'from winter.typing import is_optional\n\nimport winter.web\n\nx = winter.web.ResponseEntity\n',
    ),
    (
        'import winter\n\nx = winter.web.route_get\ny = winter.messaging.EventPublisher\n',
        'import winter.messaging\nimport winter.web\n\nx = winter.web.route_get\ny = winter.messaging.EventPublisher\n',
    ),
    (
        'import winter\n\nx = winter.web.route_get\nname = winter.__name__\n',
        'import winter\nimport winter.web\n\nx = winter.web.route_get\nname = winter.__name__\n',
    ),
    (
        'import winter.web as web\nimport winter_ddd\n\nx = web.route_get\ny = winter_ddd.AggregateRoot\n',
        'import winter.web as web\nimport winter.ddd\n\nx = web.route_get\ny = winter.ddd.AggregateRoot\n',
    ),
    (
        'import winter.core as core\n\nx = core.get_injector\n',
        'import winter.application\n\nx = winter.application.get_injector\n',
    ),
    (
        'import winter  # noqa: F401\n\nx = winter.web.route_get\n',
        'import winter.web  # noqa: F401\n\nx = winter.web.route_get\n',
    ),
    (
        'from winter.core import (\n    Component,\n    ComponentMethod,\n)\n\nx = Component, ComponentMethod\n',
        'from winter.components import Component\nfrom winter.components import ComponentMethod\n\n'
        'x = Component, ComponentMethod\n',
    ),
    (
        'from winter.core.utils.positive_integer import PositiveInteger\n'
        'from winter.core.utils.beautify_string import camel_to_human\n\nx = PositiveInteger, camel_to_human\n',
        'from winter.web.pagination.positive_integer import PositiveInteger\n'
        'from winter.web.exceptions.beautify_string import camel_to_human\n\nx = PositiveInteger, camel_to_human\n',
    ),
    (
        'from winter.data import CRUDRepository\nfrom winter.data.pagination import Page, PagePosition\n\n'
        'x = CRUDRepository, Page, PagePosition\n',
        'from winter.ddd import CRUDRepository\nfrom winter.pagination import Page\n'
        'from winter.pagination import PagePosition\n\n'
        'x = CRUDRepository, Page, PagePosition\n',
    ),
    (
        'import os\n\nimport winter.web\n\nfrom backend.models import Model\n\n'
        'winter.web.set_redis_throttling_configuration(config)\n',
        'import os\n\nimport winter.web\nfrom winter.redis.throttling import RedisThrottlingStorage\n'
        'from winter.web import set_throttling_storage\n\nfrom backend.models import Model\n\n'
        'set_throttling_storage(RedisThrottlingStorage(config))\n',
    ),
    (
        'import winter.web\nfrom .models import Model\n\nwinter.web.set_redis_throttling_configuration(config)\n',
        'import winter.web\nfrom winter.redis.throttling import RedisThrottlingStorage\n'
        'from winter.web import set_throttling_storage\nfrom .models import Model\n\n'
        'set_throttling_storage(RedisThrottlingStorage(config))\n',
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


def test_check_mode_reports_without_writing(tmp_path, capsys):
    old = tmp_path / 'old.py'
    old.write_text('import winter_ddd\n')
    unrelated = tmp_path / 'unrelated.py'
    unrelated.write_text('import os\n')

    exit_code = migrate_to_33.main(['--check', str(tmp_path)])

    assert exit_code == 1
    assert capsys.readouterr().out.strip() == str(old)
    assert old.read_text() == 'import winter_ddd\n'
