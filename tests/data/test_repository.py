from winter.data import CRUDRepository


def test_crud_repository_generic_parameters():
    class MyEntity:
        pass

    class MyRepository(CRUDRepository[MyEntity, int]):
        pass

    assert MyRepository.__entity_cls__ is MyEntity
    assert MyRepository.__primary_key_type__ is int
