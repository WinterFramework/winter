import functools
import sys


if sys.version_info > (3, 8):
    cached_property = functools.cached_property
else:
    # noinspection PyPep8Naming
    class cached_property:

        def __init__(self, func, name=None):
            self.func = func
            self.__doc__ = getattr(func, '__doc__')
            self.name = name or func.__name__

        def __get__(self, instance, cls=None):
            if instance is None:
                return self
            res = instance.__dict__[self.name] = self.func(instance)
            return res
