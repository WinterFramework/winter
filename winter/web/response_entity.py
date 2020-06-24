from http import HTTPStatus
from typing import Any

from winter.core.utils import TypeWrapper


class ResponseEntity(TypeWrapper):
    def __init__(self, entity: Any = None, status_code: int = HTTPStatus.OK):
        super().__init__()
        self._check_nested_type(type(entity))
        self.entity = entity
        self.status_code = status_code
