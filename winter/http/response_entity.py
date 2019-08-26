from http import HTTPStatus
from typing import Any


class ResponseEntity:
    def __init__(self, entity: Any = None, status_code: int = HTTPStatus.OK):
        self.entity = entity
        self.status_code = status_code
