from typing import Any
from typing import Type


class NotFoundException(Exception):
    def __init__(self, entity_id: Any, entity_cls: Type):
        self.entity_id = entity_id
        self.entity_cls = entity_cls
        super().__init__(f'{entity_cls} with ID={entity_id} not found')
