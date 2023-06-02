class Undefined:
    """A class to represent an absence of value."""
    def __eq__(self, other):
        return isinstance(other, Undefined)
