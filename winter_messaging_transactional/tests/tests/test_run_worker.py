import os
import subprocess

import pytest


def test_run_consumer_without_winter_settings_module_error():
    env = dict(
        **os.environ,
        USE_COVERAGE='true',
    )
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        subprocess.run(
            ['python', '-m', 'winter_messaging_transactional.run_consumer', 'consumer_id'],
            stderr=subprocess.PIPE,
            env=env,
            check=True,
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
            stderr=subprocess.PIPE,
            env=env,
            check=True,
        )

    called_process_error = exc_info.value
    assert called_process_error.returncode == 1
    output = called_process_error.stderr.decode('utf-8')
    assert output.find('"winter_messaging_transactional.not_exists" module could not be imported.') != -1


def test_run_consumer_with_wrong_messaging_app_config():
    env = dict(
        **os.environ,
        WINTER_SETTINGS_MODULE='winter_messaging_transactional.tests.app_sample.incorrect_app_config',
        USE_COVERAGE='true',
    )
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        subprocess.run(
            ['python', '-m', 'winter_messaging_transactional.run_consumer', 'consumer_id'],
            stderr=subprocess.PIPE,
            env=env,
            check=True,
        )

    called_process_error = exc_info.value
    assert called_process_error.returncode == 1
    output = called_process_error.stderr.decode('utf-8')
    assert output.find('Define subclass of MessagingApp and override setup method') != -1