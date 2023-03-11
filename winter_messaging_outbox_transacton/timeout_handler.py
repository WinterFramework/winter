import signal
from functools import wraps


class TimeoutException(Exception):
    pass


def raise_timeout_exception(signum, frame):
    raise TimeoutException()


class TimeoutHandler:
    can_retry = True

    @staticmethod
    def timeout(seconds: int, retries: int = 0):
        def _decorator(func):
            @wraps(func)
            def decorated_func(*args, **kwargs):
                attempts = 0
                while True:
                    signal.signal(signal.SIGALRM, raise_timeout_exception)
                    signal.setitimer(signal.ITIMER_REAL, seconds)
                    try:
                        func(*args, **kwargs)
                    except TimeoutException as e:
                        attempts += 1
                        if not TimeoutHandler.can_retry or retries < attempts:
                            raise e
                    else:
                        break
                    finally:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                        signal.signal(signal.SIGALRM, signal.SIG_DFL)

            return decorated_func

        return _decorator
