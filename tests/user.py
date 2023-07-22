import uuid


class User:
    def __init__(self, pk=None):
        self.pk = pk if pk is not None else uuid.uuid4()

    @property
    def is_authenticated(self):
        return True
