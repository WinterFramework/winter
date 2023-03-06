from dataclasses import dataclass
from uuid import UUID

import winter


@dataclass
class Note:
    name: str


class API2:
    @winter.route_patch('notes/{?note_id}')
    @winter.request_body('note')
    def update(self, note_id: UUID, note: Note):
        pass
