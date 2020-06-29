import uuid


class Entity:
    def __init__(self, id_: uuid.UUID):
        super().__init__()
        self.id = id_
