from dataclasses import dataclass
from uuid import UUID

import winter.web


@dataclass
class Note:
    name: str


class API2:
    @winter.web.route_patch('notes/{?note_id}')
    @winter.web.request_body('note')
    def update(self, note_id: UUID, note: Note):
        pass
