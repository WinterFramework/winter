import abc
import types
import typing

from .component_method import ComponentMethod


class Metadata(abc.ABC):
    key: str = None

    def __init_subclass__(cls, **kwargs):
        key = kwargs.pop('key', None)
        assert key is not None, 'Not given "key"'
        cls.key = key

    def __init__(self, value: typing.Any):
        self.value = value

    @abc.abstractmethod
    def set_value(self, metadata_storage: typing.Dict) -> None:
        pass


def metadata(metadata_: Metadata) -> types.FunctionType:
    def wrapper(func: typing.Union[types.FunctionType, ComponentMethod]):
        if isinstance(func, ComponentMethod):
            method = func
        else:
            method = ComponentMethod(func)

        method.update_metadata(metadata_)

        return method

    return wrapper
