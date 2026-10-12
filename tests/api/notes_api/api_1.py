from dataclasses import dataclass
from uuid import UUID

import winter.web


@dataclass
class Note:
    name: str


class API1:
    @winter.web.route_get('notes/{?note_id}')
    def get(self, note_id: UUID):
        pass

    @winter.web.route_post('notes/')
    @winter.web.request_body('note')
    def create(self, note: Note):
        pass
