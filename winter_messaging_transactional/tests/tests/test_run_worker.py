import os
import subprocess
from threading import Timer

import pytest
from testcontainers.rabbitmq import RabbitMqContainer


def test_run_consumer_without_winter_settings_module_error():
    env = dict(
        **os.environ,
        USE_COVERAGE='true',
    )
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        subprocess.run(
            ['python', '-m', 'winter_messaging_transactional.run_consumer', 'consumer_id'],
            capture_output=True,
            env=env,
            check=True,
            timeout=10,
        )

    called_process_error = exc_info.value
    assert called_process_error.returncode == 1
    output = called_process_error.stderr.decode('utf-8')
    assert output.find('WINTER_SETTINGS_MODULE environment variable is not set') != -1


def test_run_consumer_with_wrong_path_to_messaging_app_config():
    env = dict(
        **os.environ,
        WINTER_SETTINGS_MODULE='winter_messaging_transactional.not_exists',
        USE_COVERAGE='true',
    )
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        subprocess.run(
            ['python', '-m', 'winter_messaging_transactional.run_consumer', 'consumer_id'],
            capture_output=True,
            env=env,
            check=True,
            timeout=10,
        )

    called_process_error = exc_info.value
    assert called_process_error.returncode == 1
    output = called_process_error.stderr.decode('utf-8')
    assert output.find('"winter_messaging_transactional.not_exists" module could not be imported.') != -1


def test_run_consumer_with_wrong_messaging_app_config():
    env = dict(
        **os.environ,
        WINTER_SETTINGS_MODULE='winter_messaging_transactional.tests.incorrect_app_sample.incorrect_messaging_app',
        USE_COVERAGE='true',
    )
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        subprocess.run(
            ['python', '-m', 'winter_messaging_transactional.run_consumer', 'consumer_id'],
            capture_output=True,
            env=env,
            check=True,
            timeout=10,
        )

    called_process_error = exc_info.value
    assert called_process_error.returncode == 1
    output = called_process_error.stderr.decode('utf-8')
    assert output.find('Define subclass of MessagingApp and override setup method') != -1


def test_run_consumer_with_handler_for_event_without_topic(database_url, rabbit_url):
    env = dict(
        **os.environ,
        WINTER_SETTINGS_MODULE='winter_messaging_transactional.tests.incorrect_app_sample.messaging_app_1',
        USE_COVERAGE='true',
        WINTER_DATABASE_URL=database_url,
        WINTER_RABBIT_URL=rabbit_url,
    )
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        subprocess.run(
            ['python', '-m', 'winter_messaging_transactional.run_consumer', 'consumer'],
            capture_output=True,
            env=env,
            check=True,
            timeout=10,
        )

    called_process_error = exc_info.value
    assert called_process_error.returncode == 1
    output = called_process_error.stderr.decode('utf-8')
    expected_error = "EventWithoutTopic'>\" must be annotated with @topic for handler: \"handle_event_without_topic\""
    assert output.find(expected_error) != -1


def test_run_consumer_with_handler_for_event_with_not_declared_topic(database_url, rabbit_url):
    env = dict(
        **os.environ,
        WINTER_SETTINGS_MODULE='winter_messaging_transactional.tests.incorrect_app_sample.messaging_app_2',
        USE_COVERAGE='true',
        WINTER_DATABASE_URL=database_url,
        WINTER_RABBIT_URL=rabbit_url,
    )
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        subprocess.run(
            ['python', '-m', 'winter_messaging_transactional.run_consumer', 'consumer'],
            capture_output=True,
            env=env,
            check=True,
            timeout=10,
        )

    called_process_error = exc_info.value
    assert called_process_error.returncode == 1
    output = called_process_error.stderr.decode('utf-8')
    expected_error = "Not all topics are declared: {\'not-declared-topic\'}"
    assert output.find(expected_error) != -1


def test_run_consumer_without_rabbit_settings(database_url):
    env = dict(
        **os.environ,
        WINTER_SETTINGS_MODULE='winter_messaging_transactional.tests.incorrect_app_sample.messaging_app_2',
        USE_COVERAGE='true',
        WINTER_DATABASE_URL=database_url,
    )
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        subprocess.run(
            ['python', '-m', 'winter_messaging_transactional.run_consumer', 'consumer'],
            capture_output=True,
            env=env,
            check=True,
            timeout=10,
        )

    called_process_error = exc_info.value
    assert called_process_error.returncode == 1
    output = called_process_error.stderr.decode('utf-8')
    expected_error = "WINTER_RABBIT_URL is not set"
    assert output.find(expected_error) != -1


def test_stop_consumer_after_exception(database_url):
    rabbitmq_container = RabbitMqContainer("rabbitmq:3.11.5")
    rabbitmq_container.start()
    params = rabbitmq_container.get_connection_params()
    rabbit_url = f'amqp://{params.credentials.username}:{params.credentials.username}@{params.host}:{params.port}/'

    env = dict(
        **os.environ,
        WINTER_SETTINGS_MODULE='winter_messaging_transactional.tests.app_sample.messaging_app',
        USE_COVERAGE='true',
        WINTER_DATABASE_URL=database_url,
        WINTER_RABBIT_URL=rabbit_url,
        WINTER_RABBIT_HEARTBEAT='2',
        CONNECTION_ERROR_RETRIES_СOUNT='1'
    )

    def stop_rabbitmq():
        rabbitmq_container.stop()
    timer = Timer(interval=10, function=stop_rabbitmq)
    timer.start()

    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        subprocess.run(
            ['python', '-m', 'winter_messaging_transactional.run_consumer', 'consumer_correct'],
            capture_output=True,
            env=env,
            check=True,
            timeout=20,
        )

    called_process_error = exc_info.value
    assert called_process_error.returncode == 1
    output = called_process_error.stdout.decode('utf-8')
    assert output.find('Consumer worker consumer_correct stopping by error') != -1
    assert output.find('pika.exceptions.StreamLostError: Transport indicated EOF') != -1


