import logging
import signal
from functools import wraps
from typing import Callable

logger = logging.getLogger('event_handling')


class TimeoutException(Exception):
    pass


def raise_timeout_exception(signum, frame):
    raise TimeoutException()


class TimeoutHandler:
    def __init__(self):
        self.can_retry = True

    def timeout(self, seconds: int, retries: int = 0):
        def _decorator(func: Callable):
            @wraps(func)
            def decorated_func(*args, **kwargs):
                timeout_exception = None
                for attempts in range(1 + retries):
                    signal.signal(signal.SIGALRM, raise_timeout_exception)
                    signal.setitimer(signal.ITIMER_REAL, seconds)
                    try:
                        return func(*args, **kwargs)
                    except TimeoutException as e:
                        timeout_exception = e
                        if not self.can_retry:
                            raise timeout_exception
                        logger.warning(
                            'Timeout is raised during execution %s with args: %s, kwargs: %s',
                            func.__name__,
                            args,
                            kwargs,
                        )
                    finally:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                        signal.signal(signal.SIGALRM, signal.SIG_DFL)

                raise timeout_exception

            return decorated_func

        return _decorator
