import datetime
import importlib

import freezegun
import pytest
from docker.errors import DockerException
from testcontainers.redis import RedisContainer

import winter.web
from winter.redis.throttling import RedisThrottlingConfiguration
from winter.redis.throttling import RedisThrottlingStorage
from winter.redis.throttling import set_redis_throttling_configuration
from winter.web.throttling import get_throttling_storage
from winter.web.throttling import set_throttling_storage


@pytest.fixture(scope='module')
def redis_configuration():
    try:
        container = RedisContainer().start()
    except DockerException as e:  # pragma: no cover
        pytest.skip(f'Docker is not available: {e}')
    yield RedisThrottlingConfiguration(
        host=container.get_container_host_ip(),
        port=container.get_exposed_port(container.port),
        db=0,
        password=container.password,
    )
    container.stop()


@pytest.fixture
def keep_throttling_storage():
    previous = get_throttling_storage()
    yield
    set_throttling_storage(previous)


def test_redis_storage_sliding_window(redis_configuration):
    throttling_storage = RedisThrottlingStorage(redis_configuration)
    now = datetime.datetime.now()

    def at(seconds: float) -> bool:
        with freezegun.freeze_time(now + datetime.timedelta(seconds=seconds)):
            return throttling_storage.is_request_allowed('key', 10, 2)

    # two requests per 10 seconds; the third one inside the window is rejected and not counted
    assert [at(0), at(1), at(2), at(5)] == [True, True, False, False]
    with freezegun.freeze_time(now):
        assert throttling_storage.is_request_allowed('other key', 10, 2)

    # the requests made at 0 and 1 have left the window
    assert [at(11.5), at(12), at(12.5)] == [True, True, False]

    throttling_storage.delete('key')
    assert at(12.5)


@pytest.mark.usefixtures('keep_throttling_storage')
def test_deprecated_set_redis_throttling_configuration():
    configuration = RedisThrottlingConfiguration(host='localhost', port=6379, db=0)

    with pytest.warns(DeprecationWarning, match='set_redis_throttling_configuration is deprecated'):
        set_redis_throttling_configuration(configuration)

    assert isinstance(get_throttling_storage(), RedisThrottlingStorage)


def test_deprecated_names_in_winter_web():
    throttling_package = importlib.import_module('winter.web.throttling')  # winter.web.throttling is the decorator

    # getattr keeps tools/migrate_to_33.py from rewriting the deprecated access this test is about
    with pytest.warns(DeprecationWarning, match='winter.web.throttling.RedisThrottlingConfiguration is deprecated'):
        assert getattr(winter.web, 'RedisThrottlingConfiguration') is RedisThrottlingConfiguration
    with pytest.warns(DeprecationWarning):
        assert getattr(throttling_package, 'set_redis_throttling_configuration') is set_redis_throttling_configuration
    with pytest.raises(AttributeError):
        winter.web.no_such_name
    with pytest.raises(AttributeError):
        throttling_package.no_such_name
