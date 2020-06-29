import uuid

from winter_ddd.entity import Entity


def test_entity_sets_ids():
    class MyEntity(Entity):
        def __init__(self, id_: uuid.UUID):
            super().__init__(id_)

    entity_id = uuid.uuid4()
    my_entity = MyEntity(entity_id)
    assert my_entity.id == entity_id
