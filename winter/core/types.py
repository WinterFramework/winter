from typing import Type


class NestedTypeMeta(type):
    def __getitem__(cls, nested_type: Type) -> Type:
        assert isinstance(nested_type, type), 'nested_type should be a type'
        return type(f'{cls.__name__}[{nested_type.__name__}]', (cls,), {
            '__nested_type__': nested_type,
        })


class TypeWrapper(metaclass=NestedTypeMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not has_nested_type(self.__class__):
            raise TypeError('Using TypeWrapper without nested type is forbidden, use TypeWrapper[T]')

    def _check_nested_type(self, nested_type: Type):
        if not issubclass(nested_type, self.__nested_type__):
            raise TypeError(f'Types mismatch: {nested_type} and {self.__nested_type__}')


def has_nested_type(cls):
    return hasattr(cls, '__nested_type__')
