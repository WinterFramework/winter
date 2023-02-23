from dataclasses import dataclass
from uuid import UUID

import winter


@dataclass
class Note:
    name: str


class API1:
    @winter.route_get('notes/{?note_id}')
    def get(self, note_id: UUID):
        pass

    @winter.route_post('notes/')
    @winter.request_body('note')
    def create(self, note: Note):
        pass
