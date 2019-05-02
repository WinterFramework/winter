import uuid


class User:

    @property
    def is_authenticated(self):
        return False

    @property
    def is_anonymous(self):
        return False


class Guest(User):

    @property
    def is_anonymous(self):
        return True


class AuthorizedUser(User):

    def __init__(self, pk=None):
        self.pk = pk if pk is not None else uuid.uuid4()

    @property
    def is_authenticated(self):
        return True
