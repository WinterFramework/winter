import logging
import time
from uuid import UUID


logger = logging.getLogger('event_handling')


class EventProcessingLogger:
    def __init__(self, event_type_name: str, message_id: UUID):
        self._start_time = None
        self._event_type_name = event_type_name
        self._message_id = message_id

    def __enter__(self):
        self._start_time = time.perf_counter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_time = round(time.perf_counter() - self._start_time, 1)
        if exc_type is None:
            logger.info(
                f'{self._event_type_name} from Message({self._message_id}) is successfully processed in {elapsed_time}',
            )


