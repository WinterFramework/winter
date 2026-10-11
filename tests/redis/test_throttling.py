import datetime

import freezegun
import pytest
from docker.errors import DockerException
from testcontainers.redis import RedisContainer

from winter.redis.throttling import RedisThrottlingConfiguration
from winter.redis.throttling import RedisThrottlingStorage


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
