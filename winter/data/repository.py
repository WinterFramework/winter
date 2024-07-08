from abc import abstractmethod
from typing import Generic
from typing import Iterable
from typing import Optional
from typing import TypeVar
from typing import get_args

T = TypeVar('T')
K = TypeVar('K')


class RepositoryGenericMeta(type):
    def __init__(cls, name, bases, attr, **kwargs):
        if name not in ('Repository', 'CRUDRepository'):
            args = get_args(cls.__orig_bases__[0])
            if not args:  # pragma: no cover
                return
            if len(args) != 2:
                raise TypeError(f'Repository class takes exactly 2 generic parameters, {len(args)} were given: {args}')
            cls.__entity_cls__ = args[0]
            cls.__primary_key_type__ = args[1]
        super().__init__(name, bases, attr, **kwargs)


class Repository(Generic[T, K], metaclass=RepositoryGenericMeta):
    pass


class CRUDRepository(Repository[T, K]):
    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def delete(self, entity: T):
        pass

    @abstractmethod
    def delete_many(self, entities: Iterable[T]):
        pass

    @abstractmethod
    def delete_all(self):
        pass

    @abstractmethod
    def delete_by_id(self, id_: K):
        pass

    @abstractmethod
    def exists_by_id(self, id_: K) -> bool:
        pass

    @abstractmethod
    def find_all(self) -> Iterable[T]:
        pass

    @abstractmethod
    def find_all_by_id(self, ids: Iterable[K]) -> Iterable[T]:
        pass

    @abstractmethod
    def find_by_id(self, id_: K) -> Optional[T]:
        pass

    @abstractmethod
    def get_by_id(self, id_: K) -> T:
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        pass

    @abstractmethod
    def save_many(self, entities: Iterable[T]) -> Iterable[T]:
        pass
