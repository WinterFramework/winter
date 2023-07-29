from typing import Callable

_on_process_start_callbacks = []
_on_process_stop_callbacks = []


def on_process_start(func: Callable):
    _on_process_start_callbacks.append(func)
    return func


def on_process_stop(func: Callable):
    _on_process_stop_callbacks.append(func)
    return func


def process_start():
    for callback in _on_process_start_callbacks:
        callback()


def process_stop():
    for callback in _on_process_stop_callbacks:
        callback()
