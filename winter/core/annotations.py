class Annotations:

    def __init__(self):
        self.name = None
        self.owner = None

    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        metadata_ = instance.__dict__.get(self.name)
        if metadata_ is not None:
            return metadata_
        metadata_ = instance.__dict__[self.name] = {}
        return metadata_

    def __str__(self):
        return f'{self.__class__.__name__}({self.owner.__name__} at {self.name})'
