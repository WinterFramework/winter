import signal
from functools import wraps


class TimeoutException(Exception):
    pass


def raise_timeout_exception(signum, frame):
    raise TimeoutException()


def timeout(seconds_to_timeout: int):
    def _decorator(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            old_handler = signal.signal(signal.SIGALRM, raise_timeout_exception)
            signal.setitimer(signal.ITIMER_REAL, seconds_to_timeout)

            try:
                func(*args, **kwargs)
            finally:
                signal.signal(signal.SIGALRM, old_handler)

        return decorated_func

    return _decorator
