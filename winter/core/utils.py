# noinspection PyPep8Naming
class cached_property:

    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        if self.name in instance.__dict__:
            return instance.__dict__[self.name]
        res = instance.__dict__[self.name] = self.func(instance)
        return res

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")
