from typing import Type


class NestedTypeMeta(type):
    def __getitem__(cls, nested_type: Type) -> Type:
        assert isinstance(nested_type, type), 'nested_type should be a type'
        return type(f'{cls.__name__}[{nested_type.__name__}]', (cls,), {
            '_nested_type': nested_type,
        })


class TypeWrapper(metaclass=NestedTypeMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not has_nested_type(self.__class__):
            raise TypeError('Using TypeWrapper without nested type is forbidden, use TypeWrapper[T]')

    def _check_nested_type(self, nested_type: Type):
        if not issubclass(nested_type, self._nested_type):
            raise TypeError(f'Types mismatch: {nested_type} and {self._nested_type}')


def has_nested_type(cls):
    return hasattr(cls, '_nested_type')
