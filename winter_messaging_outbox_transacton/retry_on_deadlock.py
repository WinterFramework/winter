import logging
from functools import wraps
from typing import Callable

from psycopg2.errorcodes import DEADLOCK_DETECTED
from sqlalchemy.exc import OperationalError

logger = logging.getLogger('event_handling')


def retry_on_deadlock_decorator(attempts: int):

    def _decorator(func: Callable):

        @wraps(func)
        def decorated_func(*args, **kwargs):
            attempt_count = 0
            while attempt_count < attempts:
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    if e.orig.pgcode == DEADLOCK_DETECTED:
                        logger.error('Deadlock detected. Trying again.')
                    else:
                        raise e
                attempt_count += 1

        return decorated_func

    return _decorator


