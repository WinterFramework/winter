class Undefined:
    """A class to represent an absence of value."""
    def __eq__(self, other):
        return isinstance(other, Undefined)

    def __hash__(self):
        return 0

    def __repr__(self):
        return 'Undefined'
