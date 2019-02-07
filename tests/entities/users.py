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

    @property
    def is_authenticated(self):
        return True
