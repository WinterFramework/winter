from injector import inject
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy.engine import Engine

messaging_app_metadata = MetaData()
consumer_table = Table(
    'sample_messaging_consumers',
    messaging_app_metadata,
    Column('id', Integer, primary_key=True),
    Column('payload', String),
)


class ConsumerDAO:
    @inject
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def find_by_id(self, id_: int):
        query = select([
            consumer_table.c.id,
            consumer_table.c.payload,
        ]).where(
            consumer_table.c.id == id_,
        )
        with self._engine.connect() as connection:
            records = list(connection.execute(query))
            return dict(id=records[0].id, payload=records[0].payload) if len(records) else None

    def save(self, id_: int, payload: str):
        statement = insert(consumer_table).values(dict(id=id_, payload=payload))
        with self._engine.connect() as connection:
            connection.execute(statement)
