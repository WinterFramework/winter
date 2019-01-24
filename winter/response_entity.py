from typing import Any

import rest_framework.status as http_status


class ResponseEntity:
    def __init__(self, entity: Any = None, status_code: int = http_status.HTTP_200_OK):
        self.entity = entity
        self.status_code = status_code
